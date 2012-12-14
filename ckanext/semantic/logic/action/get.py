import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.sparql_client as sparql_client


def sparql_query(context, data_dict):
    '''
    Return a JSON formatted SPARQL endpoint response.
    
    :param query: the SPARQL query to be send to a pre-configured endpoint
    :type query: string
    :param endpoints: the endpoints to be queried
    :type endpoints: string
    
    :rtype: JSON formatted SPARQL endpoint response
    '''
    client = sparql_client.SPARQLClientFactory.create_client(sparql_client.VFClient)
    client.set_endpoints(h.get_configured_endpoints_only(data_dict['endpoints']))
    return client.query(data_dict['query'])

