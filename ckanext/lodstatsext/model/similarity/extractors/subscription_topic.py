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
            self.extract_subscription_topics(subscription)
        
        self._extracted = True


    def extract_subscription_topics(self, subscription):
        subscription_topics = None
        if subscription.definition_type == 'semantic':
            subscription_topics = self.extract_semantic_subscription_topics(subscription)
        elif subscription.definition_type == 'sparql':
            subscription_topics = self.extract_sparql_subscription_topics(subscription)
        
        if subscription_topics is not None:
            key = h.subscription_to_uri(h.user_id_to_object(subscription.owner_id).name, subscription.name)
            self.entities[key] = {'vocabularies': subscription_topics}


    def extract_semantic_subscription_topics(self, subscription):
        if subscription.definition.has_key('topics'):
            return {'vocabularies': subscription.definition['topics']}

        return None
        
            
    def extract_sparql_subscription_topics(self, semantic_subscription):
        #TODO: find a way to extract topics from a SPARQL query
        return None

