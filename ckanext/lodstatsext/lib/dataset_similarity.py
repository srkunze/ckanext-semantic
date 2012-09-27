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
import virtuoso.virtuoso as virtuoso

log = logging.getLogger(__name__)

triplestore = virtuoso.Virtuoso("localhost", "dba", "dba", 8890, "/sparql")
graph = "http://lodstats.org/"
#    print triplestore.modify('INSERT IN GRAPH <http://lodstats.org/> { <http://x.com#x> <http://x.com#y> "Juan" }')
#    print triplestore.query('select * WHERE { ?s ?p ?o filter (?s = <http://x.com#x>) }', 'json')
#    print triplestore.modify('delete from <http://lodstats.org/> { ?s ?p ?o } where { ?s ?p ?o filter (?s = <http://x.com#x>) }')



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
    
    
def get_similar_datasets(dataset_url):
    result = triplestore.query("""
                               PREFIX void: <http://rdfs.org/ns/void#>
                               SELECT ?dataset
                               FROM <""" + graph + """>
                               WHERE
                               {
                                   ?dataset a void:Dataset .
                               }
                               """)       
                                                    
    for row in result['results']['bindings']:
        print get_dataset_similarity(dataset_url, row['dataset']['value']), ': ', row['dataset']['value']


def get_dataset_similarity(dataset1_url, dataset2_url):
    vocabularies1 = get_vocabularies(dataset1_url)
    vocabularies2 = get_vocabularies(dataset2_url)

    equal = 0
    topic = 0
    common_vocabularies = []
    for vocabulary1 in vocabularies1:
        if vocabulary1 in vocabularies2:
            common_vocabularies.append(vocabulary1)
            equal += 1
            vocabulary_specifity = model.Session.query(modelext.VocabularySpecifity).get(vocabulary1)
            topic += vocabulary_specifity.specifity
    
    return topic
    
    

def get_vocabularies(dataset_url):
    result = triplestore.query("""
                               PREFIX void: <http://rdfs.org/ns/void#>
                               SELECT ?vocabulary
                               FROM <""" + graph + """>
                               WHERE
                               {
                                   ?dataset void:vocabulary ?vocabulary .
                                   filter(?dataset = <""" + dataset_url + """>)
                               }
                               """)
    return [row['vocabulary']['value'] for row in result['results']['bindings']]
