from . import EntityTime
from . import SubscriptionExtractor
import ckan.model as model
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.lib.time as ht
import ckanext.semantic.model.store as store
import datetime
import dateutil.parser


class SubscriptionTime(EntityTime, SubscriptionExtractor):
    def __init__(self):
        super(SubscriptionTime, self).__init__()


    def _extract(self):
        query = model.Session.query(model.Subscription)
        subscriptions = query.all()
        self.entities = {}
        
        for subscription in subscriptions:
            self.extract_subscription_time(subscription)
            
        self._extracted = True


    def extract_subscription_time(self, subscription):
        time = None
        type_ = subscription.definition['type']
        if type_ == 'search':
            time = self.extract_search_subscription_time(subscription)
        elif type_ == 'sparql':
            time = self.extract_sparql_subscription_time(subscription)
        
        if time is not None:
            key = h.subscription_to_uri(h.user_id_to_object(subscription.owner_id).name, subscription.name)
            self.entities[key] = time


    def extract_search_subscription_time(self, subscription):
        if 'time' in subscription.definition['filters']:
            time = subscription.definition['filters']['time']
            if time['type'] == 'span':
                return {'min_time': ht.to_naive_utc(ht.min_datetime(time['min'])),
                        'max_time': ht.to_naive_utc(ht.max_datetime(time['max']))}
                
            elif time['type'] == 'point':
                point = ht.to_naive_utc(ht.min_datetime(time['point']))
                variance = datetime.timedelta(days=int(time['variance']))

                return {'min_time': point - variance, 'max_time': point + variance}

        return None


    def extract_sparql_subscription_time(self, subscription):
        #TODO: find a way to extract time from a SPARQL query
        return None

