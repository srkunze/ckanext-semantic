from . import EntityLocation
from . import SubscriptionExtractor
import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h
import math

     
class SubscriptionLocation(EntityLocation, SubscriptionExtractor):
    def __init__(self):
        super(SubscriptionLocation, self).__init__()

        
    def _extract(self):
        query = model.Session.query(model.Subscription)
        subscriptions = query.all()
        self.entities = {}
        
        for subscription in subscriptions:
            self.extract_subscription_location(subscription)
        
        self._extracted = True


    def extract_subscription_location(self, subscription):
        subscription_location = []
        if subscription.definition_type == 'semantic':
            subscription_location = self.extract_semantic_subscription_location(subscription)
        elif subscription.definition_type == 'sparql':
            subscription_location = self.extract_sparql_subscription_location(subscription)
        
        if subscription_location is not None:
            self.entities[h.subscription_to_uri(h.user_id_to_object(subscription.owner_id).name, subscription.name)] = subscription_location


    def extract_semantic_subscription_location(self, subscription):
        if subscription.definition.has_key('location'):
            location = subscription.definition['location']
            return {'latitude': math.radians(float(location['latitude'])),
                    'longitude': math.radians(float(location['longitude'])),
                    'radius': float(location['radius'])}
            
        return None

                               
    def extract_sparql_subscription_location(self, subscription):
        #TODO: find a way to extract location from a SPARQL query
        return None

