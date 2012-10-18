from . import SimilarityMethod


class LocationSimilarity(SimilarityMethod):
    uri = 'http://www.w3.org/2003/01/geo/wgs84_pos'

    def process_similar_entity(self, similar_entity):
        square_distance = (self.entity['avgLong'] - similar_entity['avgLong'])**2 + (self.entity['avgLat'] - similar_entity['avgLat'])**2

        return None, square_distance

