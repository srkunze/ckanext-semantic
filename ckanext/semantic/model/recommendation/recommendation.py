import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.user_interests as mui
import similarity
import similarity.methods as methods


class Recommendation:
    def __init__(self, user):
        self._user_interests = mui.UserInterests(user)
        self._recommended_entity_class_uri = None
        self._count_limit = None
        self._additional_interests = set()
        self._similarity = similarity.Similarity()
        self.entities = {}
        
    def set_recommended_entity_class(self, recommended_entity_class_uri):
        self._recommended_entity_class_uri = recommended_entity_class_uri

        self._similarity.set_similar_entity_class(self._recommended_entity_class_uri)
        
        
    def set_count_limit(self, count_limit):
        self._count_limit = count_limit
    
    
    def set_additional_interests(self, additional_interests):
        self._additional_interests = additional_interests


    def set_type(self, recommendation_type):
        min_similarity_weight = 0.0
        max_similarity_distance = 0.0
        
        if recommendation_type == 'topic':
            similarity_method_class = methods.TopicSimilarity
            min_similarity_weight = 0.1
        if recommendation_type == 'location':
            similarity_method_class = methods.LocationSimilarity
            max_similarity_distance = 3
        if recommendation_type == 'time':
            similarity_method_class = methods.TimeSimilarity
            max_similarity_distance = 0.5

        self._similarity.set_similarity_method(similarity_method_class)
        self._similarity.min_similarity_weight = min_similarity_weight
        self._similarity.max_similarity_distance = max_similarity_distance

            
    def load(self):
        self.entities = {}
        not_in_database = set()
        interests = set()
        
        self._user_interests.load()
        for interest in self._user_interests.interests:
            interests.add(interest.uri)
        interests |= self._additional_interests
            
        for interest in self._user_interests.interests:
            self._similarity.set_entity(interest.uri, interest.class_uri)
            self._similarity.count_limit = 2 * self._count_limit * len(interests)

            self._similarity.load()
            
            for similar_entity, similarity_weight, similarity_distance in self._similarity.rows:
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

