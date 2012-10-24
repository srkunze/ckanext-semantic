from . import MethodData


class LocationData(MethodData):
    pass


class NormalizeToEntity(LocationData):
    def normalizer(self, entity, similar_entity):
        return entity


class NormalizeToSimilarEntity(LocationData):
    def normalizer(self, entity, similar_entity):
        return similar_entity

