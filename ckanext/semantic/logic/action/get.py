import ckanext.semantic.model.sparql_client as sparql_client


def sparql_query(context, data_dict):
    '''
    Return a JSON formatted SPARQL endpoint response.
    
    :param query: the SPARQL query to be send to a pre-configured endpoint
    :type query: string
    
    :rtype: JSON formatted SPARQL endpoint response
    '''
    client = sparql_client.SPARQLClientFactory.create_client(sparql_client.VFClient)
    client.set_endpoints(data_dict['endpoints'])
    return client.query(data_dict['query'])

