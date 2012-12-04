import ckanext.semantic.model.store as store


def sparql_query(context, data_dict):
    '''
    Return a JSON formatted SPARQL endpoint response.
    
    :param query: the SPARQL query to be send to a pre-configured endpoint
    :type query: string
    
    :rtype: JSON formatted SPARQL endpoint response
    '''
    return store.user.query(data_dict['query'], complete=True)

