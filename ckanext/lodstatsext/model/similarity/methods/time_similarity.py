class TimeSimilarity(SimilarityMethod):
    uri = 'http://www.w3.org/TR/owl-time'

    def __init__(self, time_data):
        self.time_data = time_data


    def get(self, entity, similar_entity):
        similarity_weight = None
        similarity_distance = None
        
        if max(entity['minTime'], similar_entity['minTime']) < min(entity['maxTime'], similar_entity['maxTime']):
            timedelta = min(entity['maxTime'], similar_entity['maxTime']) - max(entity['minTime'], similar_entity['minTime'])
            similarity_weight = timedelta.days * 24 * 3600 + timedelta.seconds
        else:
            timedelta = max(entity['minTime'], similar_entity['minTime']) - min(entity['maxTime'], similar_entity['maxTime'])
            similarity_distance = timedelta.days * 24 * 3600 + timedelta.seconds
        
        return similarity_weight, similarity_distance

