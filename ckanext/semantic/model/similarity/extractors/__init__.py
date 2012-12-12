class EntityExtractor(object):
    def __init__(self):
        super(EntityExtractor, self).__init__()
        self._entity_uri = None
        self._extracted = False
    
    
    def set_client(self, client):
        self._client = client


    def set_entity(self, entity_uri):
        self._entity_uri = entity_uri


    def get_entity_data(self):
        if not self._extracted:
            self._extract()
        return self.entities[self._entity_uri]


    def get_similar_entities(self, oldest_update):
        if not self._extracted:
            self._extract()
        return dict([(entity_uri, entity_data) for entity_uri, entity_data in self.entities.iteritems() if self._entity_uri == entity_uri or self.changed_since(entity_uri, oldest_update)])


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
