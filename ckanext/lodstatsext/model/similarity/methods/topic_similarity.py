from . import SimilarityMethod


class TopicSimilarity(SimilarityMethod):
    uri = 'http://xmlns.com/foaf/0.1/topic'

    def set_entity(self, entity):
        super(TopicSimilarity, self).set_entity(entity)
        self.max_similarity_weight = 0.0
        
        
    def process_similar_entity(self, similar_entity):
        similarity_weight = 0.0
        for topic in self._entity['vocabularies']:
            if topic in similar_entity['vocabularies']:
                similarity_weight += self._data.topic_weight(topic)
        
        if similarity_weight > self.max_similarity_weight:
            self.max_similarity_weight = similarity_weight
        
        return similarity_weight, None


    def post_process_result(self, similarity_weight, similarity_distance):
        if self.max_similarity_weight == 0.0:
            return similarity_weight, similarity_distance
            
        return similarity_weight / self.max_similarity_weight, similarity_distance
