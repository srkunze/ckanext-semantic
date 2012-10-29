import ckan.model as model
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.prefix as prefix
import ckanext.semantic.model.store as store
import datetime
import dateutil.parser
import extractors
import methods
import method_data
import pytz
import RDF

from . import SimilarityConfiguration


class SimilarityStats(object):
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
        
        self.count_limit = 10
        self.min_similarity_weight = None
        self.max_similarity_distance = None
        
        self._clear_rdf()
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
            
        elif self._similarity_method_class in [methods.LocationSimilarity, methods.TimeSimilarity]:
            if str(prefix.ckan.Subscription) == self._entity_class_uri:
                return method_data.NormalizeToEntity()
            if str(prefix.ckan.Subscription) == self._similar_entity_class_uri:
                return method_data.NormalizeToSimilarEntity()
            
        return None
        
        
    def _get_valid_extractor_class(self, entity_class_uri):
        return SimilarityStats.extractor_class[self._similarity_method_class][entity_class_uri]
        
        
    def _get_valid_extractor_classes(self):
        return SimilarityStats.extractor_class[self._similarity_method_class].values()


    def load(self, update_when_necessary=True):
        if self._entity_extractor is None:
            raise Exception('entity class <' + self._entity_class_uri + '> not supported')
        if self._similar_entity_extractor is None:
            raise Exception('similar entity class <' + self._similar_entity_class_uri + '> not supported')

        self._increase_request_count()

        if update_when_necessary and self._update_necessary():
            print "similarity update for", self._entity_uri, self._similarity_method.uri
            self.update()
                
        self._load()
        
        
    def _increase_request_count(self):
        configuration = self._get_configuration()
            
        configuration.request_count += 1
        
        model.Session.merge(configuration)
        model.Session.commit()


    def _update_necessary(self):
        relevant_count = 50
        valid_age = 7
        
        configuration = self._get_configuration()
        
        if configuration.created is None:
            similarity_count, oldest_created = self.get_similarity_count_and_oldest_created()
            
            brand_new = similarity_count == 0
            oft_requested = configuration.request_count > relevant_count
            too_less = 2 * self.count_limit > similarity_count
                
            return brand_new or oft_requested or too_less


        entity_changed = self._entity_extractor.changed_since(self._entity_uri, configuration.created)
        too_old = (datetime.datetime.now() - configuration.created).days > valid_age
        oft_requested = configuration.request_count > relevant_count

        return entity_changed or too_old and oft_requested
        
      
    def get_similarity_count_and_oldest_created(self):
        row = store.root.query('''
                               prefix sim: <http://purl.org/ontology/similarity/>
                               select (count(?similarity) as ?similarity_count) (min(?created) as ?oldest_created)
                               where
                               {
                                   ?similarity a sim:Similarity.
                                   ?similarity sim:method <''' + self._similarity_method.uri + '''>.
                                   ?similarity sim:element <''' + self._entity_uri + '''>.
                                   ?similarity <http://purl.org/dc/terms/created> ?created.
                               }
                               ''')[0]

        similarity_count = None
        oldest_created = None

        if row.has_key('similarity_count'):
            similarity_count = int(row['similarity_count']['value'])
        if row.has_key('oldest_created'):
            oldest_created = dateutil.parser.parse(row['oldest_created']['value'])
        
        return similarity_count, oldest_created


    def _load(self):
        filter_string = ''
        if self.min_similarity_weight is not None or self.max_similarity_distance is not None:
            filter_string += 'filter('
            if self.min_similarity_weight is not None:
                filter_string += '?similarity_weight >= ' + str(self.min_similarity_weight)
            
            if self.min_similarity_weight is not None and self.max_similarity_distance is not None:
                filter_string += ' or '

            #HINT: xs:decimal doesn't support infinity
            if self.max_similarity_distance is not None:
                filter_string += '?similarity_distance <= ' + str(self.max_similarity_distance)
            filter_string += ')'
        
        #FIXME: owl:Thing problem to determine class of entity1
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
                                    ''' + filter_string + '''
                                }
                                order by desc(?similarity_weight) ?similarity_distance
                                limit ''' + str(self.count_limit) + '''
                                ''')
        
        self.rows = [(row['similar_entity']['value'],
                      row['similarity_weight']['value'] if row.has_key('similarity_weight') else None,
                      row['similarity_distance']['value'] if row.has_key('similarity_distance') else None) for row in rows]

       
    def update(self):
        results = {}

        try:
            self._entity_extractor.set_entity(self._entity_uri)
            entity_data = self._entity_extractor.get_entity_data()
        except KeyError:
            self._update_timestamp()
            return
        self._similarity_method.set_entity(entity_data)


        #TODO: remove code duplication in function _update_necessary
        #TODO: remove unclean code method invocation
        configuration = self._get_configuration()
        if self._entity_extractor.changed_since(self._entity_uri, configuration.created):
            similar_entities = self._similar_entity_extractor.get_similar_entities(None)
        else:
            similar_entities = self._similar_entity_extractor.get_similar_entities(configuration.created)
            
        
        for similar_entity_uri, similar_entity_data in similar_entities.iteritems():
            results[similar_entity_uri] = self._similarity_method.process_similar_entity(similar_entity_data)

        for similar_entity_uri, result in results.iteritems():
            similarity_weight, similarity_distance = self._similarity_method.post_process_result(*result)
            
            #TODO: filtering similarities by min and max should be reflected in configuration
            if similarity_weight is not None and self.min_similarity_weight is not None and similarity_weight < self.min_similarity_weight or \
               similarity_distance is not None and self.max_similarity_distance is not None and similarity_distance > self.max_similarity_distance:
               #continue
               pass
            
            # no nice way of updating a similarity with only one element
            if self._entity_uri != similar_entity_uri:
               self._commit(similar_entity_uri, similarity_weight, similarity_distance)
        
        self._update_timestamp()


    def _commit(self, similar_entity_uri, similarity_weight=None, similarity_distance=None):
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

        store.root.modify(graph=self.graph,
                          insert_construct=h.rdf_to_string(self.rdf),
                          delete_construct='?similarity ?predicate ?object.',
                          delete_where='''
                          ?similarity <http://purl.org/ontology/similarity/element> <''' + self._entity_uri + '''>.
                          ?similarity <http://purl.org/ontology/similarity/element> <''' + similar_entity_uri + '''>.
                          ?similarity <http://purl.org/ontology/similarity/method> <''' + self._similarity_method.uri + '''>.
                          ?similarity ?predicate ?object.
                          ''')
        
        self._clear_rdf()
        
        
    def _update_timestamp(self):
        configuration = self._get_configuration()
            
        configuration.created = datetime.datetime.now()
        configuration.request_count = 1
        
        model.Session.merge(configuration)
        model.Session.commit()
        
        
    def _get_configuration(self):
        configuration = model.Session.query(SimilarityConfiguration).get((self._entity_uri, self._similarity_method.uri))

        if configuration is None:
            return SimilarityConfiguration(self._entity_uri, self._similarity_method.uri)
            
        return configuration


    def _clear_rdf(self):
        self.rdf = RDF.Model()

