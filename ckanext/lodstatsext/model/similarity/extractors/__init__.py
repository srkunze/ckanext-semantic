class EntityExtractor(object):
    def get(self, entity_uri):
        return self.entities[entity_uri]
        
        
    def get_all(self):
        return self.entities


    def count(self):
        return len(self.entities)


from entity_topic import EntityTopic
from entity_location import EntityLocation
from entity_time import EntityTime

from dataset_extractor import DatasetExtractor
from dataset_topic import DatasetTopic
from dataset_location import DatasetLocation
from dataset_time import DatasetTime

from subscription_extractor import SubscriptionExtractor
from subscription_topic import SubscriptionTopic
from subscription_location import SubscriptionLocation
from subscription_time import SubscriptionTime
