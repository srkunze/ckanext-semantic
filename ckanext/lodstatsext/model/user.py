import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.prefix as prefix


class User:
    def __init__(self, user):
        self.user = user
        self.interests = []


    def load_interests(self):
        query = model.Session.query(model.Package)
        query = query.join(model.UserFollowingUser, model.Package.id == model.UserFollowingUser.object_id)
        query = query.filter(model.UserFollowingUser.follower_id == self.user.id)
        datasets = query.all()
        
        for dataset in datasets:
            dataset.uri = h.dataset_to_uri(dataset.name)
            dataset.class_uri = str(prefix.void.Dataset.uri)
        
        query = model.Session.query(model.Subscription)
        query = query.filter(model.Subscription.owner_id == self.user.id)
        subscriptions = query.all()

        for subscription in subscriptions:
            subscription.uri = h.subscription_to_uri(self.user.name, subscription.name)
            subscription.class_uri = str(prefix.ckan.Subscription.uri)

        
        self.interests = datasets + subscriptions
