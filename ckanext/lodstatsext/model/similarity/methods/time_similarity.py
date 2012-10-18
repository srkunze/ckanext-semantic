from . import SimilarityMethod


class TimeSimilarity(SimilarityMethod):
    uri = 'http://www.w3.org/TR/owl-time'

    def process_similar_entity(self, similar_entity):
        similarity_weight = None
        similarity_distance = None
        
        if max(self.entity['minTime'], similar_entity['minTime']) < min(self.entity['maxTime'], similar_entity['maxTime']):
            timedelta = min(self.entity['maxTime'], similar_entity['maxTime']) - max(self.entity['minTime'], similar_entity['minTime'])
            similarity_weight = timedelta.days * 24 * 3600 + timedelta.seconds
        else:
            timedelta = max(self.entity['minTime'], similar_entity['minTime']) - min(self.entity['maxTime'], similar_entity['maxTime'])
            similarity_distance = timedelta.days * 24 * 3600 + timedelta.seconds
        
        return similarity_weight, similarity_distance

