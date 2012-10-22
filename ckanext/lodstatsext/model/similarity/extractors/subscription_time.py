from . import EntityTime
from . import SubscriptionExtractor
import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.store as store
import datetime
import dateutil.parser


class SubscriptionTime(EntityTime, SubscriptionExtractor):
    def __init__(self):
        query = model.Session.query(model.Subscription)
        subscriptions = query.all()
        self.entities = {}
        
        for subscription in subscriptions:
            self.extract_subscription_time(subscription)


    def extract_subscription_time(self, subscription):
        subscription_time = None
        if subscription.definition_type == 'semantic':
            subscription_time = self.extract_semantic_subscription_time(subscription)
        elif subscription.definition_type == 'sparql':
            subscription_time = self.extract_sparql_subscription_time(subscription)
        
        if subscription_time is not None:
            self.entities[h.subscription_to_uri(h.user_id_to_object(subscription.owner_id).name, subscription.name)] = subscription_time


    def extract_semantic_subscription_time(self, subscription):
        if subscription.definition.has_key('time'):
            time = subscription.definition['time']
            if time['type'] == 'span':
                return {'minTime': dateutil.parser.parse(time['min']), 'maxTime': dateutil.parser.parse(time['max'])}
            elif time['type'] == 'point':
                point = dateutil.parser.parse(semantic['time']['point'])
                variance = datetime.timedelta(days=int(semantic['time']['variance']))
                min_ = point - variance
                max_ = point + variance
                return {'minTime': min_, 'maxTime': max_}

        return None


    def extract_sparql_subscription_time(self, subscription):
        #TODO: find a way to extract time from a SPARQL query
        return None

