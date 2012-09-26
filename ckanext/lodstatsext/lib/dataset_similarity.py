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

log = logging.getLogger(__name__)

sparql = sparql_wrapper.SPARQLWrapper("http://localhost:8890/sparql")
sparql.setReturnFormat(sparql_wrapper.JSON)


def update_vocabulary_specifity():
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


def dataset_similarity():
    sparql.setQuery("""
                    prefix void: <http://rdfs.org/ns/void#>
                    SELECT (count(distinct ?dataset) as ?dataset_count)
                    WHERE
                    {
                        ?dataset a void:Dataset .
                    }
                    """)   
    results2 = sparql.query().convert()
    
     
    return
    
    
