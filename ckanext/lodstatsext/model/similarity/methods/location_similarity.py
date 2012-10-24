from . import SimilarityMethod
import math


class LocationSimilarity(SimilarityMethod):
    uri = 'http://www.w3.org/2003/01/geo/wgs84_pos'

    def process_similar_entity(self, similar_entity):
        min_radius = min(similar_entity['radius'], self._entity['radius']) + 1.0
        max_radius = max(similar_entity['radius'], self._entity['radius']) + 1.0
        
        radius_sum = min_radius + max_radius
        distance = self._distance(self._entity['latitude'], self._entity['longitude'],
                                  similar_entity['latitude'], similar_entity['longitude'])
        difference = radius_sum - distance
        
        if difference <= 0:
            similarity_distance = -difference
            
            return None, similarity_distance / ((self._data.normalizer(self._entity, similar_entity)['radius'] + 1.0) if self._data is not None else 1.0)

        return min(2 * min_radius, difference) / (2 * max_radius), None
        

    def _distance(self, latitude1, longitude1, latitude2, longitude2):
        latitude_haversine = self.haversine(latitude1 - latitude2)
        longitude_haversine = self.haversine(longitude1 - longitude2)
        
        earth_radius = 6378.0
        s = latitude_haversine + math.cos(latitude1) * math.cos(latitude2) * longitude_haversine
        distance = 2 * earth_radius * math.asin(min(1.0, math.sqrt(s)))

        return distance


    def haversine(self, x):
        return (1 - math.cos(x)) / 2

