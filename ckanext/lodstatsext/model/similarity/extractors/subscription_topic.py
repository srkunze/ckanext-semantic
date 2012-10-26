from . import EntityTopic
from . import SubscriptionExtractor
import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h

     
class SubscriptionTopic(EntityTopic, SubscriptionExtractor):
    def __init__(self):
        super(SubscriptionTopic, self).__init__()


    def _extract(self):
        query = model.Session.query(model.Subscription)
        subscriptions = query.all()
        self.entities = {}
        
        for subscription in subscriptions:
            self.extract_subscription_topic(subscription)
        
        self._extracted = True


    def extract_subscription_topic(self, subscription):
        topic = None
        type_ = subscription.definition['type']
        if type_ == 'search':
            topic = self.extract_search_subscription_topic(subscription)
        elif type_ == 'sparql':
            topic = self.extract_sparql_subscription_topic(subscription)
        
        if topic is not None:
            key = h.subscription_to_uri(h.user_id_to_object(subscription.owner_id).name, subscription.name)
            self.entities[key] = topic

    def extract_search_subscription_topic(self, subscription):
        if 'topic' in subscription.definition['filters']:
            topic = subscription.definition['filters']['topic']
            return {'vocabularies': topic}

        return None
        
            
    def extract_sparql_subscription_topic(self, subscription):
        #TODO: find a way to extract the topic from a SPARQL query
        return None

