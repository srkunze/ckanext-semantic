from . import EntityLocation
import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h

     
class SubscriptionLocation(EntityLocation):
    def __init__(self):
        query = model.Session.query(model.Subscription)
        #query = query.filter(model.Subscription.owner_id == self.user.id)
        subscriptions = query.all()
        self.entities = {}
        
        for subscription in subscriptions:
            self.extract_subscription_location(subscription)


    def extract_subscription_location(self, subscription):
        subscription_location = []
        if subscription.definition_type == 'semantic':
            subscription_location = self.extract_semantic_subscription_location(subscription)
        elif subscription.definition_type == 'sparql':
            subscription_location = self.extract_sparql_subscription_location(subscription)
        
        if subscription_location is not None:
            self.entities[h.subscription_to_uri(subscription.owner, subscription.name)] = subscription_location


    def extract_semantic_subscription_location(self, subscription):
        if subscription.definition.has_key('location'):
            location = subscription.definition['location']
            return {'avgLat': location['latitude'], 'avgLong': location['longitude']}
            
        return None

                               
    def extract_sparql_subscription_location(self, subscription):
        #TODO: find a way to extract location from a SPARQL query
        return None

