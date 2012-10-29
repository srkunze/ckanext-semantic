class MethodData(object):
    pass


class NormalizeToEntity(MethodData):
    def normalizer(self, entity, similar_entity):
        return entity


class NormalizeToSimilarEntity(MethodData):
    def normalizer(self, entity, similar_entity):
        return similar_entity


from topic_data import SpecificityWeightedTopic
from topic_data import EqualWeightedTopic
