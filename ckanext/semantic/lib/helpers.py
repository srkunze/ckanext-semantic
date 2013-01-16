import ckan.model as model
import pylons
import RDF
import re
import urllib



root = 'http://localhost:5000/'
path_to_dataset = 'dataset/'
path_to_user = 'user/'
path_to_subscription = 'subscription/'
serializer = RDF.Serializer(name='ntriples')

            
def dataset_to_uri(dataset_name):
    return root + path_to_dataset + dataset_name
    
          
def user_to_uri(user_name):
    return root + path_to_user + user_name        

          
def subscription_to_uri(user_name, subscription_name):
    return root + path_to_user + user_name + '/' + path_to_subscription + urllib.quote(subscription_name)


def user_id_to_object(user_id):
    return model.Session.query(model.User).get(user_id)


def user_name_to_object(user_name):
    return model.Session.query(model.User).filter(model.User.name == user_name).one()


def rdf_to_string(rdf):
    return serializer.serialize_model_to_string(rdf)
    
    
def uri_to_object(uri_string):
    match = re.search(root + path_to_dataset + '(.*)', uri_string)
    if match is not None:
        return model.Session.query(model.Package).filter(model.Package.name == match.group(1)).one()
        
    match = re.search(root + path_to_user + '(.*)/' + path_to_subscription + '(.*)', uri_string)
    if match is not None:
        query = model.Session.query(model.Subscription)
        query = query.filter(model.Subscription.name == urllib.unquote(match.group(2)))
        query = query.filter(model.Subscription.owner_id == user_name_to_object(match.group(1)).id)
        return query.one()

    match = re.search(root + path_to_user + '(.*)', uri_string)
    if match is not None:
        return model.Session.query(model.User).filter(model.User.name == match.group(1)).one()


def get_endpoints(type_, with_name=False):
    if type_ == 'standard':
        return [_get_standard_endpoint(with_name)]
    if type_ == 'additional':
        return _get_additional_endpoints(with_name)
    return [_get_standard_endpoint(with_name)] + _get_additional_endpoints(with_name)


def _get_standard_endpoint(with_name):
    if with_name:
        return (pylons.config.get('ckan.semantic.SPARQL_endpoint_standard'), pylons.config.get('ckan.semantic.SPARQL_endpoint_standard_name'))
    return pylons.config.get('ckan.semantic.SPARQL_endpoint_standard')


def _get_additional_endpoints(with_name):
    endpoints = []
    for index in range(0, 20):
        endpoint_url = pylons.config.get('ckan.semantic.SPARQL_endpoint_additional_%s' % index, None)
        if not endpoint_url:
            break
        if with_name:
            endpoint = (endpoint_url, pylons.config.get('ckan.semantic.SPARQL_endpoint_additional_%s_name' % index))
        else:
            endpoint = endpoint_url
        endpoints.append(endpoint)
    return endpoints


def get_configured_endpoints_only(endpoints):
    available_endpoints = get_endpoints(type_='all')
    chosen_endpoints = []
    for endpoint in endpoints:
        if endpoint in available_endpoints:
            chosen_endpoints.append(endpoint)
    return chosen_endpoints
