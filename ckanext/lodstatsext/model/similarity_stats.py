import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import ckanext.lodstatsext.model.dataset_wrapper as dw
import ckanext.lodstatsext.model.location_similarity_stats as lss
import datetime
import dateutil.parser
import pytz
import RDF


class SimilarityStats:
    def __init__(self,
                 similarity_method,
                 element_uri,
                 element_class_uri = 'http://rdfs.org/ns/void#Dataset',
                 similar_element_class_uri = 'http://rdfs.org/ns/void#Dataset',
                 graph='http://lodstats.org/similarities'):

        self.similarity_method = similarity_method
        self.element_uri = element_uri
        self.element_class_uri = element_class_uri
        self.similar_element_class_uri = similar_element_class_uri
        self.rdf = RDF.Model()
        self.rows = []
        self.graph = graph
        self.store = triplestore.ts


    def load(self, count_limit, update_when_necessary=False):
        if not update_when_necessary and self.update_necessary():
            self.update_and_commit()
            
        self._load_from_store_only(count_limit)


    def update_necessary(self):          
        real, min_created = self.get_real_count_min_created()
        possible = self.possible_count()
        
        #TODO: configurable
        too_old = (datetime.datetime.now(pytz.utc) - min_created).days > 7
        too_less = float(real) / float(possible) < 0.4
        
        return too_old or too_less
     

    def get_real_count_min_created(self):
        row = self.store.query('''
                               prefix sim: <http://purl.org/ontology/similarity/>
                               select (count(distinct ?element1) as ?count) (min(?created) as ?min_created)
                               where
                               {
                                   ?similarity a sim:Similarity.
                                   ?similarity sim:method <''' + self.similarity_method.uri + '''>.
                                   ?similarity sim:element ?element1.
                                   ?similarity sim:element ?element2.
                                   ?similarity <http://purl.org/dc/terms/created> ?created.
                                   filter(?element2=<''' + self.element_uri + '''> and ?element1!=?element2)
                               }
                               ''')[0]
        if row.has_key('min_created'):
            min_created = dateutil.parser.parse(row['min_created']['value'])
        else:
            min_created = datetime.datetime.now(pytz.utc)
            
        return int(row['count']['value']), min_created
        
    def possible_count(self):
        return self.similarity_method.dataset.count()

    
    def _load_from_store_only(self, count_limit):
        #FIXME: owl:Thing problem to determine class of element1
        #FIXME: xs:decimal(-1) necessary for virtuoso 6.1
        rows = self.store.query('''
                                prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                prefix sim: <http://purl.org/ontology/similarity/>
                                select ?similar_element (if(bound(?weight), ?weight, (if(bound(?distance), ?distance, xs:decimal(-1)))) as ?similarity_value)
                                where
                                {
                                    ?similarity a sim:Similarity.
                                    ?similarity sim:method <''' + self.similarity_method.uri + '''>.
                                    ?similarity sim:element ?element.
                                    ?similarity sim:element ?similar_element.
                                    ?similar_element a <''' + self.similar_element_class_uri + '''>
                                    optional
                                    {
                                        ?similarity sim:weight ?weight.
                                    }
                                    optional
                                    {
                                        ?similarity sim:distance ?distance.
                                    }
                                    filter(?element = <''' + self.element_uri + '''> and
                                           ?element != ?similar_element)
                                }
                                order by desc(?weight) ?distance
                                limit ''' + str(count_limit) + '''
                                ''')
        
        self.rows = [(row['similar_element']['value'], row['similarity_value']['value']) for row in rows]

       
    def update_and_commit(self):
        self.update()
        self.commit()


    def update(self):
        if self.element_class_uri == 'http://rdfs.org/ns/void#Dataset':
            element_data = self.similarity_method.dataset.get(self.element_uri)
            similar_elements = self.similarity_method.dataset.get_all()
        else:
            raise Exception('element class <' + self.element_class_uri + '> not supported')

        for similar_element_uri, similar_element_data in similar_elements.iteritems():
            similarity_weight, similarity_distance = self.similarity_method.get(element_data, similar_element_data)
            self.append(similar_element_uri, similarity_weight, similarity_distance)
             
            
    def append(self, similar_element_uri, similarity_weight=None, similarity_distance=None):
        similarity_node = RDF.Node()
        self.rdf.append(RDF.Statement(similarity_node, prefix.rdf.type, prefix.sim.Similarity))
        self.rdf.append(RDF.Statement(similarity_node, prefix.dct.created, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.method, RDF.Uri(self.similarity_method.uri)))

        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(self.element_uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(similar_element_uri)))

        if similarity_weight is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.weight, RDF.Node(literal=str(similarity_weight), datatype=prefix.xs.decimal.uri)))
        if similarity_distance is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.distance, RDF.Node(literal=str(similarity_distance), datatype=prefix.xs.decimal.uri)))

        

    def commit(self):
        serializer = RDF.Serializer(name="ntriples")
        triples = serializer.serialize_model_to_string(self.rdf)
        self.store.modify('''
                          delete from graph <''' + self.graph + '''>
                          {
                              ?similarity ?predicate ?object.
                          }
                          where
                          {
                              ?similarity a <http://purl.org/ontology/similarity/Similarity>.
                              ?similarity <http://purl.org/ontology/similarity/element> <''' + self.element_uri + '''>.
                              ?similarity <http://purl.org/ontology/similarity/method> <''' + self.similarity_method.uri + '''>.
                              ?similarity ?predicate ?object.
                          }
                          
                          insert in graph <''' + self.graph + '''>
                          {
                          ''' + triples + '''
                          }
                          ''')

    def clear_rdf(self):
        self.rdf = RDF.Model()

