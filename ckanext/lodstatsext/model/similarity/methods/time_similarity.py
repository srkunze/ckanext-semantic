from . import SimilarityMethod


class TimeSimilarity(SimilarityMethod):
    uri = 'http://www.w3.org/TR/owl-time'

    def process_similar_entity(self, similar_entity):
        similarity_weight = None
        similarity_distance = None
        
        entity_timedelta = TimeSimilarity.at_least_1_day(self._entity['max_time'] - self._entity['min_time'])
        similar_entity_timedelta = TimeSimilarity.at_least_1_day(similar_entity['max_time'] - similar_entity['min_time'])
        
        max_min_time = max(self._entity['min_time'], similar_entity['min_time'])
        min_max_time = min(self._entity['max_time'], similar_entity['max_time'])
        
        print max_min_time, min_max_time
        
        timedelta = TimeSimilarity.at_least_1_day(max_min_time - min_max_time)
        print max_min_time - min_max_time
        print timedelta
        
        if timedelta > 0:
            similarity_distance = timedelta / self._normalizer(entity_timedelta, similar_entity_timedelta)
        else:
            similarity_weight = -timedelta / max(entity_timedelta, similar_entity_timedelta)

        return similarity_weight, similarity_distance


    def _normalizer(self, entity_timedelta, similar_entity_timedelta):
        if self._data is None:
            return 1.0

        return float(max(1, self._data.normalizer(entity_timedelta, similar_entity_timedelta) / 2))


    @classmethod
    def at_least_1_day(cls, timedelta):
        if timedelta.days <= 0:
            return float(min(-1, timedelta.days))
            
        return float(max(1, timedelta.days))

