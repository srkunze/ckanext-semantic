import ckan.logic as logic
import ckan.lib.dictization.model_dictize as model_dictize
import datetime
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.store as store


def sparql_dataset(context, data_dict):
    results = store.user.query(data_dict['query'], complete=True)
    
    if isinstance(results, str):
        return results

    return results


def subscription_sparql_dataset(context, data_dict):
    results = sparql_dataset({}, data_dict)

    if isinstance(results, str):
        return []
        
    return results['results']['bindings'], None


def subscription_sparql_dataset_list(context, data_dict):
    if 'user' not in context:
        raise ckan.logic.NotAuthorized
    model = context['model']
    user = model.User.get(context['user'])
    if not user:
        raise ckan.logic.NotAuthorized

    
    if 'subscription_id' in data_dict:
        subscription_id = logic.get_or_bust(data_dict, 'subscription_id')
        query = model.Session.query(model.Subscription)
        query = query.filter(model.Subscription.id==subscription_id)

    elif 'subscription_name' in data_dict:
        subscription_name = logic.get_or_bust(data_dict, 'subscription_name')
        query = model.Session.query(model.Subscription)
        query = query.filter(model.Subscription.owner_id==user.id)
        query = query.filter(model.Subscription.name==subscription_name)
    
    subscription = query.one()
    
    # to be up-to-date, please refactor
    if subscription.last_evaluated < datetime.datetime.now() - datetime.timedelta(minutes=1):
        logic.get_action('subscription_item_list_update')(context, data_dict)
        
    datasets = []
    if subscription.definition['type'] == 'sparql':
        for item in subscription.get_item_list():
            for key, value in item.data.iteritems():
                if value['type'] == 'uri':
                    object_ = h.uri_to_object(value['value'])
                    if isinstance(object_, model.Package):
                        datasets.append(model_dictize.package_dictize(object_, context))
    
    return datasets
