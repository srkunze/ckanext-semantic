import ckan.model as model

     
class SubscriptionTopic(EntityTopic):
    def __init__(self):
        query = model.Session.query(model.Subscription)
        #query = query.filter(model.Subscription.owner_id == self.user.id)
        subscriptions = query.all()

        for subscription in subscriptions:
            extract_subscription_topics(subscription)


    def extract_subscription_topics(subscription):
        subscription_topics = []
        if subscription.definition_type == 'semantic':
            subscription_topics = extract_semantic_subscription_topics(subscription)
        elif subscription.definition_type == 'sparql':
            subscription_topics = extract_sparql_subscription_topics(subscription)
        
        if subscription_time is not None:
            self.entities[subscription.id] = subscription_topics


    def extract_semantic_subscription_topics(subscription):
        subscription.parse_definition()

        return subscription.definition['topics']
        
            
    def extract_sparql_subscription_topics(semantic_subscription):
        #TODO: find a way to extract topics from a SPARQL query
        return None

