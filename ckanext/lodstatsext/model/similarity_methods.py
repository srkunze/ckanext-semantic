import dataset_wrapper as dw


class TopicSimilarity:
    uri = 'http://xmlns.com/foaf/0.1/topic'
    dataset = dw.DatasetTopic

    @classmethod
    def get(cls, vocabularies1, vocabularies2):
        similarity_weight = 0
        for vocabulary1 in vocabularies1.keys():
            if vocabulary1 in vocabularies2:
                similarity_weight += vocabularies1[vocabulary1]
                
        return similarity_weight, None


class LocationSimilarity:
    uri = 'http://www.w3.org/2003/01/geo/wgs84_pos'
    dataset = dw.DatasetLocation

    @classmethod
    def get(cls, element, similar_element):
        square_distance = (element['avgLong'] - similar_element['avgLong'])**2 + (element['avgLat'] - similar_element['avgLat'])**2

        return None, square_distance


class TimeSimilarity:
    uri = 'http://www.w3.org/TR/owl-time'
    dataset = dw.DatasetTime

    @classmethod
    def get(cls, element, similar_element):
        similarity_weight = None
        similarity_distance = None
        
        if max(element['minTime'], similar_element['minTime']) < min(element['maxTime'], similar_element['maxTime']):
            timedelta = min(element['maxTime'], similar_element['maxTime']) - max(element['minTime'], similar_element['minTime'])
            similarity_weight = timedelta.days * 24 * 3600 + timedelta.seconds
        else:
            timedelta = max(element['minTime'], similar_element['minTime']) - min(element['maxTime'], similar_element['maxTime'])
            similarity_distance = timedelta.days * 24 * 3600 + timedelta.seconds
        
        return similarity_weight, similarity_distance

