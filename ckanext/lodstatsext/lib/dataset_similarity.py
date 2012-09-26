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


def update_vocabulary_specifity():
    sparql = sparql_wrapper.SPARQLWrapper("http://localhost:8890/sparql")
    sparql.setQuery("""
                    prefix void: <http://rdfs.org/ns/void#>
                    SELECT ?vocab (count(?dataset) as ?x)
                    WHERE
                    {
                        ?dataset a void:Dataset .
                        ?dataset void:vocabulary ?vocab .
                    }
                    group by ?vocab
                    order by desc(?x)
                    """)
    sparql.setReturnFormat(sparql_wrapper.JSON)
    results = sparql.query().convert()

    for row in results['results']['bindings']:
        print row["vocab"]["value"], ": ", row["x"]["value"]
        
    model.Session.add(dataset_lodstats)
    model.Session.commit()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    return
    
