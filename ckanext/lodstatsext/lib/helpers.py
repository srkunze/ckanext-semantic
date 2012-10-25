import ckan.model as model
import RDF
import re
import urllib

host = 'http://localhost:5000/'
path_to_dataset = 'dataset/'
path_to_user = 'user/'
path_to_subscription = 'subscription/'
serializer = RDF.Serializer(name='ntriples')

            
def dataset_to_uri(dataset_name):
    return host + path_to_dataset + dataset_name
    
          
def user_to_uri(user_name):
    return host + path_to_user + user_name        

          
def subscription_to_uri(user_name, subscription_name):
    return host + path_to_user + user_name + '/' + path_to_subscription + urllib.quote(subscription_name)


def user_id_to_object(user_id):
    return model.Session.query(model.User).get(user_id)


def user_name_to_object(user_name):
    return model.Session.query(model.User).filter(model.User.name == user_name).one()


def rdf_to_string(rdf):
    return serializer.serialize_model_to_string(rdf)
    
    
def uri_to_object(uri_string):
    match = re.search(host + path_to_dataset + '(.*)', uri_string)
    if match is not None:
        return model.Session.query(model.Package).filter(model.Package.name == match.group(1)).one()
        
    match = re.search(host + path_to_user + '(.*)/' + path_to_subscription + '(.*)', uri_string)
    if match is not None:
        query = model.Session.query(model.Subscription)
        query = query.filter(model.Subscription.name == urllib.unquote(match.group(2)))
        query = query.filter(model.Subscription.owner_id == user_name_to_object(match.group(1)).id)
        return query.one()

    match = re.search(host + path_to_user + '(.*)', uri_string)
    if match is not None:
        return model.Session.query(model.User).filter(model.User.name == match.group(1)).one()

