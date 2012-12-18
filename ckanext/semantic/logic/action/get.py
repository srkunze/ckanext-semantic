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
    '''
    client = sparql_client.SPARQLClientFactory.create_client(sparql_client.VFClient, 'standard')
    results = client.query_list('''
    prefix void: <http://rdfs.org/ns/void#>
    SELECT distinct ?uri ?type ?label
    WHERE
    {
        {
            ?x void:vocabulary ?uri.
            ?x ?type ?uri.
        }
        union
        {
            ?x void:class ?uri.
            ?x ?type ?uri.
        }
        union
        {
            ?x void:property ?uri.
            ?x ?type ?uri.
        }
        optional
        {
            ?uri <http://purl.org/dc/terms/title> ?label.
        }
        filter(fn:contains(fn:lower-case(?uri), fn:lower-case("%s")))
    }
''' % data_dict['query'], datatypes={'uri': str, 'type': str, 'label': str})

    uri_to_label = {
        'http://rdfs.org/ns/void#vocabulary': 'vocabulary',
        'http://rdfs.org/ns/void#class': 'class',
        'http://rdfs.org/ns/void#property': 'property',
    }

    z = []
    for result in results:
        uri = result['uri']
        type_ = uri_to_label[result['type']]
        label = result.get('label', '')
        z.append({'uri': uri, 'type': type_, 'label': label})

    x = []
    return json.dumps(z)
    # LOV endpoint doesn't support JSON
    # FedX cannot handle endpoint either so
    # start workaround
    r = requests.get('http://lov.okfn.org/endpoint/lov?query=SELECT%20%3Flabel%20%3Furi%0AWHERE%0A%7B%0A%20%20%20%20%3Furi%20a%20%3Chttp%3A%2F%2Fpurl.org%2Fvocommons%2Fvoaf%23Vocabulary%3E.%0A%20%20%20%20%3Furi%20%3Chttp%3A%2F%2Fpurl.org%2Fvocab%2Fvann%2FpreferredNamespacePrefix%3E%20%3Fprefix.%0A%20%20%20%20%3Furi%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2Ftitle%3E%20%3Flabel.%0A%20%20%20%20filter(fn%3Acontains(fn%3Alower-case(%3Furi)%2C%20fn%3Alower-case(%22ab%22)))%0A%7D&format=SPARQL')
    result = dom_parser.parseString(r.text.encode('utf-8'))
    rows = result.getElementsByTagName('result')
    for row in rows:
        bindings = row.getElementsByTagName('binding')
        y = {}
        x.append(y)
        for binding in bindings:
            for type_ in ['literal', 'uri', 'bnode']:
                z = binding.getElementsByTagName(type_)
                if z.length == 1:
                    y[binding.getAttribute('name')] = z.item(0).firstChild.data
                    break
    # end workaround
    #print x


    return json.dumps(z)
