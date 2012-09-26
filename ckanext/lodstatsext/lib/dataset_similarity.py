import ckan.model as model
import ckan.model.meta as meta
import ckanext.lodstatsext.model.dataset_similarity as modelext
import datetime
import lodstats
import logging
import os
import RDF
import SPARQLWrapper as sparql_wrapper
import sqlalchemy
import pycurl

log = logging.getLogger(__name__)




def update_vocabulary_specifity():
    sparql = sparql_wrapper.SPARQLWrapper("http://localhost:8890/sparql")
    sparql.setReturnFormat(sparql_wrapper.JSON)
    sparql.setQuery("""
                    prefix void: <http://rdfs.org/ns/void#>
                    SELECT ?vocabulary (count(?dataset) as ?dataset_count)
                    WHERE
                    {
                        ?dataset a void:Dataset .
                        ?dataset void:vocabulary ?vocabulary .
                    }
                    group by ?vocabulary
                    order by desc(?dataset_count)
                    """)
    results1 = sparql.query().convert()
    
    sparql.setQuery("""
                    prefix void: <http://rdfs.org/ns/void#>
                    SELECT (count(distinct ?dataset) as ?dataset_count)
                    WHERE
                    {
                        ?dataset a void:Dataset .
                    }
                    """)
    results2 = sparql.query().convert()

    for row in results1['results']['bindings']:
        vocabulary_specifity = modelext.VocabularySpecifity(row["vocabulary"]["value"])
        vocabulary_specifity.specifity = 1 - (float(row["dataset_count"]["value"]) / float(results2['results']['bindings'][0]["dataset_count"]["value"]))
        vocabulary_specifity.dataset_count = int(row["dataset_count"]["value"])
        model.Session.merge(vocabulary_specifity)   

    model.Session.commit()        

    return


def get_dataset_similarity():
    import virtuoso.virtuoso as virtuoso
    
    
    triplestore = virtuoso.Virtuoso("localhost", "dba", "dba", 8890, "/sparql")
    
    from rdflib import Namespace, Literal

    graph = "http://lodstats.org/"
    ns = Namespace("http://x.com#")
    triplestore.insert(graph, ns["x"], ns["y"], Literal("Juan"))
    print triplestore.endpoint.query('SELECT * WHERE {?s ?p "Juan"}')[0]['s'].value
    print triplestore.endpoint.query('SELECT (count(*) as ?count) WHERE {?s ?p "Juan"}')[0]['count'].value
    triplestore.delete(graph, ns["x"], ns["y"], Literal("Juan"))
    print triplestore.endpoint.query('SELECT (count(*) as ?count) WHERE {?s ?p "Juan"}')[0]['count'].value


    return
    

  
