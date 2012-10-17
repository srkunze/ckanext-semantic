class LocationSimilarity(SimilarityMethod):
    uri = 'http://www.w3.org/2003/01/geo/wgs84_pos'

    def __init__(self, location_data):
        self.location_data = location_data

    
    def get(self, entity, similar_entity):
        square_distance = (entity['avgLong'] - similar_entity['avgLong'])**2 + (entity['avgLat'] - similar_entity['avgLat'])**2

        return None, square_distance

