import ckan.model as model
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.prefix as prefix


class UserInterests:
    def __init__(self, user):
        self.user = user
        self.interests = []


    def load(self):
        query = model.Session.query(model.Package)
        query = query.join(model.UserFollowingDataset, model.Package.id == model.UserFollowingDataset.object_id)
        query = query.filter(model.UserFollowingDataset.follower_id == self.user.id)
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
