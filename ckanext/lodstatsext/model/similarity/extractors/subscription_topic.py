from . import EntityTopic
import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h

     
class SubscriptionTopic(EntityTopic):
    def __init__(self):
        query = model.Session.query(model.Subscription)
        #query = query.filter(model.Subscription.owner_id == self.user.id)
        subscriptions = query.all()
        self.entities = {}
        
        for subscription in subscriptions:
            self.extract_subscription_topics(subscription)


    def extract_subscription_topics(self, subscription):
        subscription_topics = []
        if subscription.definition_type == 'semantic':
            subscription_topics = self.extract_semantic_subscription_topics(subscription)
        elif subscription.definition_type == 'sparql':
            subscription_topics = self.extract_sparql_subscription_topics(subscription)
        
        if subscription_topics is not None:
            self.entities[h.subscription_to_uri(subscription.owner_id, subscription.name)] = subscription_topics


    def extract_semantic_subscription_topics(self, subscription):
        if subscription.definition.has_key('topics'):
            return subscription.definition['topics']

        return None
        
            
    def extract_sparql_subscription_topics(self, semantic_subscription):
        #TODO: find a way to extract topics from a SPARQL query
        return None
