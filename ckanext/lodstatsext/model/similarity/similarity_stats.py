import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.store as store
import datetime
import dateutil.parser
import pytz
import RDF


class SimilarityStats:
    def __init__(self,
                 similarity_method,
                 entity_uri,
                 entity_class_uri = 'http://rdfs.org/ns/void#Dataset',
                 similar_entity_class_uri = 'http://rdfs.org/ns/void#Dataset',
                 graph='http://lodstats.org/similarities'):

        self.similarity_method = similarity_method
        self.entity_uri = entity_uri
        self.entity_class_uri = entity_class_uri
        self.similar_entity_class_uri = similar_entity_class_uri
        self.rdf = RDF.Model()
        self.rows = []
        self.graph = graph


    def load(self, count_limit, update_when_necessary=True):
        if update_when_necessary and self.update_necessary():
            self.update_and_commit()
                
        self._load(count_limit)


    def update_necessary(self):          
        real, min_created = self._get_real_count_min_created()
        possible = self._possible_count()
        
        #TODO: configurable
        too_old = (datetime.datetime.now(pytz.utc) - min_created).days > 7
        too_less = float(real) / float(possible) < 0.4
        
        return too_old or too_less
     

    def _get_real_count_min_created(self):
        row = store.root.query('''
                               prefix sim: <http://purl.org/ontology/similarity/>
                               select (count(distinct ?entity1) as ?count) (min(?created) as ?min_created)
                               where
                               {
                                   ?similarity a sim:Similarity.
                                   ?similarity sim:method <''' + self.similarity_method.uri + '''>.
                                   ?similarity sim:element ?entity1.
                                   ?similarity sim:element ?entity2.
                                   ?similarity <http://purl.org/dc/terms/created> ?created.
                                   filter(?entity2=<''' + self.entity_uri + '''> and ?entity1!=?entity2)
                               }
                               ''')[0]
        if row.has_key('min_created'):
            min_created = dateutil.parser.parse(row['min_created']['value'])
        else:
            min_created = datetime.datetime.now(pytz.utc)
            
        return int(row['count']['value']), min_created
        
    def _possible_count(self):
        return self.similarity_method.dataset.count()

    
    def _load(self, count_limit):
        #FIXME: owl:Thing problem to determine class of entity1
        #FIXME: xs:decimal(-1) necessary for virtuoso 6.1
        rows = store.root.query('''
                                prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                prefix sim: <http://purl.org/ontology/similarity/>
                                select ?similar_entity ?similarity_weight ?similarity_distance
                                where
                                {
                                    ?similarity a sim:Similarity.
                                    ?similarity sim:method <''' + self.similarity_method.uri + '''>.
                                    ?similarity sim:element ?entity.
                                    ?similarity sim:element ?similar_entity.
                                    ?similar_entity a <''' + self.similar_entity_class_uri + '''>
                                    optional
                                    {
                                        ?similarity sim:weight ?similarity_weight.
                                    }
                                    optional
                                    {
                                        ?similarity sim:distance ?similarity_distance.
                                    }
                                    filter(?entity = <''' + self.entity_uri + '''> and
                                           ?entity != ?similar_entity)
                                }
                                order by desc(?similarity_weight) ?similarity_distance
                                limit ''' + str(count_limit) + '''
                                ''')
        
        self.rows = [(row['similar_entity']['value'],
                      row['similarity_weight']['value'],
                      row['similarity_distance']['value']) for row in rows]

       
    def update_and_commit(self):
        self.update()
        self.commit()


    def update(self):
        similarity_method = self.similarity_method_class()
        
        if self.entity_class_uri == str(prefix.void.Dataset):
            entity_data = self.similarity_method.dataset.get(self.entity_uri)
        elif self.entity_class_uri == str(prefix.void.Subscription):
            entity_data = self.similarity_method.subscription.get(self.entity_uri)
        else:
            raise Exception('entity class <' + self.entity_class_uri + '> not supported')

        if self.similar_entity_class_uri == str(prefix.void.Dataset):
            similar_elements = self.similarity_method.dataset.get_all()
        else:
            raise Exception('similar entity class <' + self.entity_class_uri + '> not supported')

        for similar_entity_uri, similar_entity_data in similar_elements.iteritems():
            similarity_weight, similarity_distance = self.similarity_method.get(entity_data, similar_entity_data)
            self.append(similar_entity_uri, similarity_weight, similarity_distance)
             
            
    def append(self, similar_entity_uri, similarity_weight=None, similarity_distance=None):
        similarity_node = RDF.Node()
        self.rdf.append(RDF.Statement(similarity_node, prefix.rdf.type, prefix.sim.Similarity))
        self.rdf.append(RDF.Statement(similarity_node, prefix.dct.created, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.method, RDF.Uri(self.similarity_method.uri)))

        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(self.entity_uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(similar_entity_uri)))

        if similarity_weight is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.weight, RDF.Node(literal=str(similarity_weight), datatype=prefix.xs.decimal.uri)))
        if similarity_distance is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.distance, RDF.Node(literal=str(similarity_distance), datatype=prefix.xs.decimal.uri)))

        

    def commit(self):
        store.root.modify(self.graph,
                          h.rdf_to_string(triples),
                          '?similarity ?predicate ?object.',
                          '''
                          ?similarity a <http://purl.org/ontology/similarity/Similarity>.
                          ?similarity <http://purl.org/ontology/similarity/element> <''' + self.entity_uri + '''>.
                          ?similarity <http://purl.org/ontology/similarity/method> <''' + self.similarity_method.uri + '''>.
                          ?similarity ?predicate ?object.
                          ''')

    def clear_rdf(self):
        self.rdf = RDF.Model()

