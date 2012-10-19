import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.store as store
import datetime
import dateutil.parser
import extractors
import methods
import method_data
import pytz
import RDF


class SimilarityStats:
    extractor_class = {methods.TopicSimilarity:{str(prefix.void.Dataset): extractors.DatasetTopic, str(prefix.ckan.Subscription): extractors.SubscriptionTopic},
                       methods.LocationSimilarity:{str(prefix.void.Dataset): extractors.DatasetLocation, str(prefix.ckan.Subscription): extractors.SubscriptionLocation},
                       methods.TimeSimilarity:{str(prefix.void.Dataset): extractors.DatasetTime, str(prefix.ckan.Subscription): extractors.SubscriptionTime}}


    def __init__(self, graph='http://lodstats.org/similarities'):
        self._similarity_method = None
        self._similarity_method_class = None
        self._entity_uri = None
        self._entity_class_uri = None
        self._entity_extractor = None
        self._similar_entity_class_uri = None
        self._similar_entity_extractor = None
        
        self.rdf = RDF.Model()
        self.rows = []
        self.graph = graph


    def set_entity(self, entity_uri, entity_class_uri):
        self._entity_uri = entity_uri

        if self._entity_class_uri == entity_class_uri:
            return
        
        self._entity_class_uri = entity_class_uri
        self._set_similarity_method_data()
        
        if self._similar_entity_class_uri == self._entity_class_uri:
            self._entity_extractor = self._similar_entity_extractor
            return
        
        self._set_entity_extractor()
        

    def _set_entity_extractor(self):
        self._entity_extractor = self._get_extractor(self._entity_class_uri)


    def set_similar_entity_class(self, similar_entity_class_uri):
        if self._similar_entity_class_uri == similar_entity_class_uri:
            return

        self._similar_entity_class_uri = similar_entity_class_uri
        self._set_similarity_method_data()

        if self._entity_class_uri == self._similar_entity_class_uri:
            self._similar_entity_extractor = self._entity_extractor
            return

        self._set_similar_entity_extractor()
        
        
    def _set_similar_entity_extractor(self):
        self._similar_entity_extractor = self._get_extractor(self._similar_entity_class_uri)


    def _get_extractor(self, entity_class_uri):
        try:
            extractor_class = self._get_valid_extractor_class(entity_class_uri)

            return extractor_class()
        except KeyError:
            pass

        return None
        

    def set_similarity_method(self, similarity_method_class):
        self._similarity_method = similarity_method_class()
        self._similarity_method_class = similarity_method_class
        
        self._set_similarity_method_data()
        
        valid_extractor_classes = self._get_valid_extractor_classes()
        if self._entity_extractor.__class__ not in valid_extractor_classes:
            self._set_entity_extractor()
        if self._similar_entity_extractor.__class__ not in valid_extractor_classes:
            self._set_similar_entity_extractor()
        

    def _set_similarity_method_data(self):
        if self._similarity_method is None:
            return
            
        self._similarity_method.set_method_data(self._get_method_data())


    def _get_method_data(self):
        if self._similarity_method_class == methods.TopicSimilarity:
            if str(prefix.ckan.Subscription) in [self._entity_class_uri, self._similar_entity_class_uri]:
                return method_data.EqualWeightedTopic()
            return method_data.SpecificityWeightedTopic(str(prefix.vstats.cosSpecificity))
            
        return None
        
        
    def _get_valid_extractor_class(self, entity_class_uri):
        return SimilarityStats.extractor_class[self._similarity_method_class][entity_class_uri]
        
        
    def _get_valid_extractor_classes(self):
        return SimilarityStats.extractor_class[self._similarity_method_class].values()


    def load(self, count_limit, update_when_necessary=True):
        if self._entity_extractor is None:
            raise Exception('entity class <' + self._entity_class_uri + '> not supported')
        if self._similar_entity_extractor is None:
            raise Exception('similar entity class <' + self._similar_entity_class_uri + '> not supported')

        if update_when_necessary and self._update_necessary():
            self._update_and_commit()
                
        self._load(count_limit)


    def _update_necessary(self):          
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
                                   ?similarity sim:method <''' + self._similarity_method.uri + '''>.
                                   ?similarity sim:element ?entity1.
                                   ?similarity sim:element ?entity2.
                                   ?similarity <http://purl.org/dc/terms/created> ?created.
                                   filter(?entity2=<''' + self._entity_uri + '''> and ?entity1!=?entity2)
                               }
                               ''')[0]
        if row.has_key('min_created'):
            min_created = dateutil.parser.parse(row['min_created']['value'])
        else:
            min_created = datetime.datetime.now(pytz.utc)
            
        return int(row['count']['value']), min_created


    def _possible_count(self):
        return self._similar_entity_extractor.count()

    
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
                                    ?similarity sim:method <''' + self._similarity_method.uri + '''>.
                                    ?similarity sim:element <''' + self._entity_uri + '''>.
                                    ?similarity sim:element ?similar_entity.
                                    ?similar_entity a <''' + self._similar_entity_class_uri + '''>
                                    optional
                                    {
                                        ?similarity sim:weight ?similarity_weight.
                                    }
                                    optional
                                    {
                                        ?similarity sim:distance ?similarity_distance.
                                    }
                                    filter(<''' + self._entity_uri + '''> != ?similar_entity)
                                }
                                order by desc(?similarity_weight) ?similarity_distance
                                limit ''' + str(count_limit) + '''
                                ''')
        
        self.rows = [(row['similar_entity']['value'],
                      row['similarity_weight']['value'] if row.has_key('similarity_weight') else None,
                      row['similarity_distance']['value'] if row.has_key('similarity_distance') else None) for row in rows]

       
    def _update_and_commit(self):
        self._update()
        self._commit()


    def _update(self):
        results = {}

        try:
            entity = self._entity_extractor.get(self._entity_uri)
        except KeyError:
            return
        self._similarity_method.set_entity(entity)

        similar_entities = self._similar_entity_extractor.get_all()
        for similar_entity_uri, similar_entity_data in similar_entities.iteritems():
            results[similar_entity_uri] = self._similarity_method.process_similar_entity(similar_entity_data)

        for similar_entity_uri, result in results.iteritems():
            similarity_weight, similarity_distance  = self._similarity_method.post_process_result(*result)
            self._append(similar_entity_uri, similarity_weight, similarity_distance)

   
    def _append(self, similar_entity_uri, similarity_weight=None, similarity_distance=None):
        similarity_node = RDF.Node()
        self.rdf.append(RDF.Statement(similarity_node, prefix.rdf.type, prefix.sim.Similarity))
        self.rdf.append(RDF.Statement(similarity_node, prefix.dct.created, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.method, RDF.Uri(self._similarity_method.uri)))

        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(self._entity_uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(similar_entity_uri)))

        if similarity_weight is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.weight, RDF.Node(literal=str(similarity_weight), datatype=prefix.xs.decimal.uri)))
        if similarity_distance is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.distance, RDF.Node(literal=str(similarity_distance), datatype=prefix.xs.decimal.uri)))

        

    def _commit(self):
        store.root.modify(self.graph,
                          h.rdf_to_string(self.rdf),
                          '?similarity ?predicate ?object.',
                          '''
                          ?similarity a <http://purl.org/ontology/similarity/Similarity>.
                          ?similarity <http://purl.org/ontology/similarity/element> <''' + self._entity_uri + '''>.
                          ?similarity <http://purl.org/ontology/similarity/method> <''' + self._similarity_method.uri + '''>.
                          ?similarity ?predicate ?object.
                          ''')

