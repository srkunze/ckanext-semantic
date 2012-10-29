class SimilarityMethod(object):
    def __init__(self):
        self._entity = None
        self._data = None


    def set_entity(self, entity):
        self._entity = entity


    def set_method_data(self, data):
        self._data = data
        
        
    def post_process_result(self, similarity_weight, similarity_distance):
        return similarity_weight, similarity_distance


from topic_similarity import TopicSimilarity
from location_similarity import LocationSimilarity
from time_similarity import TimeSimilarity
