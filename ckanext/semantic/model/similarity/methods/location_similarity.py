from . import SimilarityMethod
import ckanext.semantic.lib.location as hl


class LocationSimilarity(SimilarityMethod):
    uri = 'http://stats.lod2.eu/resource/geographical-similarity-method'

    def process_similar_entity(self, similar_entity):
        similarity_weight = None
        similarity_distance = None

        min_radius = min(similar_entity['radius'], self._entity['radius']) + 1.0
        max_radius = max(similar_entity['radius'], self._entity['radius']) + 1.0
        
        radius_sum = min_radius + max_radius
        distance = hl.distance(self._entity['latitude'], self._entity['longitude'],
                              similar_entity['latitude'], similar_entity['longitude'])
        difference = distance - radius_sum
        
        if difference >= 0:
            similarity_distance = difference / self._normalizer(self._entity, similar_entity)
        else:
            similarity_weight = min(2 * min_radius, -difference) / (2 * max_radius)
            
        return similarity_weight, similarity_distance
        
        
    def _normalizer(self, entity, similar_entity):
        if self._data is None:
            return 1.0

        return self._data.normalizer(entity, similar_entity)['radius'] + 1.0

