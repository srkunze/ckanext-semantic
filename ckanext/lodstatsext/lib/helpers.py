import ckan.model as model
import RDF

host = 'http://localhost:5000/'
path_to_dataset = 'dataset/'
path_to_user = 'user/'
path_to_subscription = 'subscription/'
serializer = RDF.Serializer(name='ntriples')


def uri_to_object(uri_string):
    if uri_string.find(host + path_to_dataset) == 0:
        x = uri_string.replace(host + path_to_dataset, '', 1)
        return model.Session.query(model.Package).filter(model.Package.name == x).one()
        
    if uri_string.find(host + path_to_user) == 0:
        x = uri_string.replace(host + path_to_user, '', 1)
        return model.Session.query(model.User).filter(model.User.name == x).one()
        
          
def dataset_to_uri(dataset_name):
    return host + path_to_dataset + dataset_name
    
          
def user_to_uri(user_name):
    return host + path_to_user + user_name        

          
def subscription_to_uri(user_name, subscription_name):
    return host + path_to_user + user_name + '/' + path_to_subscription + subscription_name        


def rdf_to_string(triples):
    return serializer.serialize_model_to_string(self.rdf)
