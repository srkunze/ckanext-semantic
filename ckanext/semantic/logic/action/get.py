import ckan.logic as logic
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.sparql_client as sparql_client
import requests
import xml.dom.minidom as dom_parser
import json

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


def uri_suggestions(context, data_dict):
    '''
    Return a list of URIs.
    
    param query: search terms
    type query: string
    
    rtype: JSON formatted URIs list
    '''
    client = sparql_client.SPARQLClientFactory.create_client(sparql_client.VFClient, 'standard')
    results = client.query_list('''
    prefix void: <http://rdfs.org/ns/void#>
    SELECT distinct ?uri ?category ?label
    WHERE
    {
        {
            ?x void:vocabulary ?uri.
            ?x ?category ?uri.
        }
        union
        {
            ?x void:class ?uri.
            ?x ?category ?uri.
        }
        union
        {
            ?x void:property ?uri.
            ?x ?category ?uri.
        }
        optional
        {
            ?uri <http://purl.org/dc/terms/title> ?label.
        }
        filter(fn:contains(fn:lower-case(?uri), fn:lower-case("%s")))
    }
''' % data_dict['query'], datatypes={'uri': str, 'category': str, 'label': str})

    uri_to_category = {
        'http://rdfs.org/ns/void#vocabulary': 'vocabulary',
        'http://rdfs.org/ns/void#class': 'class',
        'http://rdfs.org/ns/void#property': 'property',
    }

    z = []
    for result in results:
        uri = result['uri']
        category = uri_to_category[result['category']]
        label = result.get('label', '')
        z.append({'uri': uri, 'category': category, 'label': label})

    return z
