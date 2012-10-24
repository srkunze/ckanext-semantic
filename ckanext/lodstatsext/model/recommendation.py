import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.store as store
import ckanext.lodstatsext.model.user as mu
import similarity
import similarity.methods as methods


class Recommendation:
    def __init__(self, user):
        self._user = mu.User(user)
        self._recommended_entity_class_uri = None
        self._count_limit = None
        self._similarity_stats = similarity.SimilarityStats()
        self.entities = {}
        
    def set_recommended_entity_class(self, recommended_entity_class_uri):
        self._recommended_entity_class_uri = recommended_entity_class_uri

        self._similarity_stats.set_similar_entity_class(self._recommended_entity_class_uri)
        
        
    def set_count_limit(self, count_limit):
        self._count_limit = count_limit


    def set_type(self, recommendation_type):
        min_similarity_weight = None
        max_similarity_distance = None
        
        if recommendation_type == 'topic':
            similarity_method_class = methods.TopicSimilarity
            min_similarity_weight = 0.1
        if recommendation_type == 'location':
            similarity_method_class = methods.LocationSimilarity
            max_similarity_distance = 3
        if recommendation_type == 'time':
            similarity_method_class = methods.TimeSimilarity
            max_similarity_distance = 365

        self._similarity_stats.set_similarity_method(similarity_method_class)
        self._similarity_stats.min_similarity_weight = min_similarity_weight
        self._similarity_stats.max_similarity_distance = max_similarity_distance

            
    def load(self):
        self.entities = {}
        not_in_database = set()
        interests = set()
        
        self._user.load_interests()
        for interest in self._user.interests:
            interests.add(interest.uri)
            #TODO: add subscription items
            
        for interest in self._user.interests:
            self._similarity_stats.set_entity(interest.uri, interest.class_uri)
            self._similarity_stats.count_limit = 2 * self._count_limit * len(self._user.interests)

            self._similarity_stats.load()
            
            for similar_entity, similarity_weight, similarity_distance in self._similarity_stats.rows:
                if similar_entity in not_in_database or similar_entity in interests:
                    continue

                entity_object = h.uri_to_object(similar_entity)
                if entity_object is None:
                    not_in_database.add(similar_entity)
                    continue
                    
                if self.entities.has_key(entity_object):
                    self.entities[entity_object].append(interest)
                else:
                    self.entities[entity_object] = [interest]

        self.entities = dict(sorted(self.entities.iteritems(), key=lambda entity: len(entity[1]), reverse=True)[:self._count_limit])

