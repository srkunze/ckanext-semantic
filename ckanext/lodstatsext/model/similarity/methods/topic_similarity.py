class TopicSimilarity(SimilarityMethod):
    uri = 'http://xmlns.com/foaf/0.1/topic'

    def __init__(self, topic_data):
        self.topic_data = topic_data


    def get(self, entity, similar_entity):
        similarity_weight = 0
        for topic in entity:
            if topic in similar_entity:
                similarity_weight += self.topic_data.topic_weight(topic)
                
        return similarity_weight, None

