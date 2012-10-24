from . import SimilarityMethod
import ckanext.lodstatsext.lib.time as h


class TimeSimilarity(SimilarityMethod):
    uri = 'http://www.w3.org/TR/owl-time'

    def process_similar_entity(self, similar_entity):
        similarity_weight = None
        similarity_distance = None
        
        entity_timedelta = self._entity['maxTime'] - self._entity['minTime']
        similar_entity_timedelta = similar_entity['maxTime'] - similar_entity['minTime']
        max_timedelta = max(entity_timedelta, similar_entity_timedelta)
        
        max_min_time = max(self._entity['minTime'], similar_entity['minTime'])
        min_max_time = min(self._entity['maxTime'], similar_entity['maxTime'])
        
        timedelta = min_max_time - max_min_time
        
        if max_min_time > min_max_time:
            similarity_distance = h.seconds(-timedelta) / self._normalizer(entity_timedelta, similar_entity_timedelta)
        else:
            similarity_weight = h.seconds(timedelta) / h.seconds(max_timedelta)
        
        return similarity_weight, similarity_distance


    def _normalizer(self, entity_timedelta, similar_entity_timedelta):
        if self._data is None:
            return 1.0

        return h.seconds(self._data.normalizer(entity_timedelta, similar_entity_timedelta)) / 2

