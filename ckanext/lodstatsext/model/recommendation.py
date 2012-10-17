import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.store as store
import ckanext.lodstatsext.model.user as mu
import similarity.similarity_stats as sss
import similarity.methods as methods

class Recommendation:
    def __init__(self, user):
        self.user = mu.User(user)
        self.count_limit = 5
        self.entities = []
        
        
    def set_count_limit(self, count_limit):
        self.count_limit = count_limit


    def datasets(self, similarity_method_name):
        if similarity_method_name == 'topic':
            similarity_method = sm.TopicSimilarity
        if similarity_method_name == 'location':
            similarity_method = sm.LocationSimilarity
        if similarity_method_name == 'time':
            similarity_method = sm.TimeSimilarity
            
        self._entities_by_class(str(prefix.void.Dataset.uri), similarity_method)
        return self.entities

        
    def _entities_by_class(self, recommended_entity_class_uri, similarity_method):
        self.entities = {}
        not_in_database = set()
        interests = set()
        
        self.user.load_interests()
        for interest in self.user.interests:
            interests[interest.uri] = 'interest'
            
        for interest in self.user.interests:
            similarities = sss.SimilarityStats(similarity_method, interest.uri,
                                               interest.class_uri, recommended_entity_class_uri)
            similarities.load(self.count_limit * len(self.user.interests)) # <<< in order to get sufficiently relevant entities
            
            for similar_entity, similarity_weight, similarity_distance in similarities.rows:
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
