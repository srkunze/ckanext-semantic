import ckan.model as model


host = 'http://localhost:5000/'
path_to_dataset = 'dataset/'
path_to_user = 'user/'


def uri_to_db_object(uri_string):
    if uri_string.find(host + path_to_dataset) == 0:
        x = uri_string.replace(host + path_to_dataset, '', 1)
        return model.Session.query(model.Package).filter(model.Package.name == x).one()
        
    if uri_string.find(host + path_to_user) == 0:
        x = uri_string.replace(host + path_to_user, '', 1)
        return model.Session.query(model.User).filter(model.User.name == x).one()
        
          
def dataset_to_uri(datasetname):
    return host + path_to_dataset + datasetname
    
          
def user_to_uri(username):
    return host + path_to_user + username        
        
