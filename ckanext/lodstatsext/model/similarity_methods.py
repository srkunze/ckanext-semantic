import ckanext.lodstatsext.model.dataset_wrapper as dw


class TopicSimilarity:
    uri = 'http://xmlns.com/foaf/0.1/topic'
    dataset = dw.DatasetTopic

    @classmethod
    def get(cls, entity, similar_entity):
        similarity_weight = 0
        for vocabulary in entity.keys():
            if vocabulary in similar_entity:
                similarity_weight += entity[vocabulary]
                
        return similarity_weight, None


class LocationSimilarity:
    uri = 'http://www.w3.org/2003/01/geo/wgs84_pos'
    dataset = dw.DatasetLocation

    @classmethod
    def get(cls, entity, similar_entity):
        square_distance = (entity['avgLong'] - similar_entity['avgLong'])**2 + (entity['avgLat'] - similar_entity['avgLat'])**2

        return None, square_distance


class TimeSimilarity:
    uri = 'http://www.w3.org/TR/owl-time'
    dataset = dw.DatasetTime

    @classmethod
    def get(cls, entity, similar_entity):
        similarity_weight = None
        similarity_distance = None
        
        if max(entity['minTime'], similar_entity['minTime']) < min(entity['maxTime'], similar_entity['maxTime']):
            timedelta = min(entity['maxTime'], similar_entity['maxTime']) - max(entity['minTime'], similar_entity['minTime'])
            similarity_weight = timedelta.days * 24 * 3600 + timedelta.seconds
        else:
            timedelta = max(entity['minTime'], similar_entity['minTime']) - min(entity['maxTime'], similar_entity['maxTime'])
            similarity_distance = timedelta.days * 24 * 3600 + timedelta.seconds
        
        return similarity_weight, similarity_distance

