import ckanext.semantic.lib.helpers as h


class SubscriptionExtractor(object):
    def __init__(self):
        super(SubscriptionExtractor, self).__init__()


    def changed_since(self, entity_uri, oldest_update):
        if oldest_update is None:
            return True
        subscription = h.uri_to_object(entity_uri)
        return subscription.last_modified > oldest_update
