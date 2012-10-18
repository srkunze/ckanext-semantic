class SimilarityMethod(object):
    def set_method_data(self, data):
        self.data = data
        
        
    def set_entity(self, entity):
        self.entity = entity


    def post_process_result(self, similarity_weight, similarity_distance):
        return similarity_weight, similarity_distance


from topic_similarity import TopicSimilarity
from location_similarity import LocationSimilarity
from time_similarity import TimeSimilarity
