import ckan.model as model

     
class SubscriptionLocation(EntityLocation):
    def __init__(self):
        query = model.Session.query(model.Subscription)
        #query = query.filter(model.Subscription.owner_id == self.user.id)
        subscriptions = query.all()

        for subscription in subscriptions:
            extract_subscription_location(subscription)


    def extract_subscription_location(subscription):
        subscription_location = []
        if subscription.definition_type == 'semantic':
            subscription_location = extract_semantic_subscription_location(subscription)
        elif subscription.definition_type == 'sparql':
            subscription_location = extract_sparql_subscription_location(subscription)
        
        if subscription_time is not None:
            self.entities[subscription.id] = subscription_location


    def extract_semantic_subscription_location(semantic_subscription):
        subscription.parse_definition()
        location = subscription.definition['location']

        return {'avgLat': location['latitude'], 'avgLong': location['longitude']}

                               
    def extract_semantic_sparql_location(semantic_subscription):
        #TODO: find a way to extract location from a SPARQL query
        return None

