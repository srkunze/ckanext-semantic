import ckan.model as model
import ckan.model.meta as meta
import ckanext.lodstatsext.model.similarity_stats as model_similarity_stats
import ckanext.lodstatsext.model.triplestore as triplestore
import datetime
import lodstats
import logging
import math
import os
import RDF
import sqlalchemy

log = logging.getLogger(__name__)



def update_dataset_similarities(dataset_uri_string, similarity_uri_string):
    if similarity_uri_string == 'http://lodstats.org/similarity#topic':
        result = triplestore.ts.query('''
                                   prefix vstats: <http://lodstats.org/vocabulary#>
                                   prefix void: <http://rdfs.org/ns/void#>
                                   prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                   
                                   select ?dataset2 (sum(xs:decimal(?specificity)) as ?similarity)
                                   where
                                   {
                                       <''' + dataset_uri_string + '''> void:vocabulary ?vocabulary1.
                                       ?dataset2 a void:Dataset.
                                       ?dataset2 void:vocabulary ?vocabulary2.
                                       
                                       ?vocabulary1 <http://lodstats.org/vocabulary#cosSpecificity> ?specificity.
                                       filter(?vocabulary1=?vocabulary2)
                                   }
                                   group by ?dataset2
                                   order by desc(?similarity)
                                   ''')       

        similarity_stats = model_similarity_stats.SimilarityStats()
                                                  
        for row in result['results']['bindings']:
            similarity_stats.append(dataset_uri_string, row['dataset2']['value'], row['similarity']['value'], 'http://lodstats.org/similarity#topic')
        
        similarity_stats.commit()
        
    elif similarity_uri_string == 'http://lodstats.org/similarity#vocabulary':
        pass
    elif similarity_uri_string == 'http://lodstats.org/similarity#location':
        pass
    elif similarity_uri_string == 'http://lodstats.org/similarity#time':
        pass


def get_similar_datasets(dataset_url, similarity_uri_string, count):
    result = triplestore.ts.query('''
                               prefix lsvs: <http://lodstats.org/vocabulary-specificity#>
                               prefix void: <http://rdfs.org/ns/void#>
                               prefix xs: <http://www.w3.org/2001/XMLSchema#>
                               
                               select ?dataset2 (sum(xs:decimal(?specificity)) as ?similarity)
                               from <http://lodstats.org/vocabulary-specificity/>
                               where
                               {
                                   <''' + dataset_url + '''> void:vocabulary ?vocabulary1.
                                   ?dataset2 a void:Dataset.
                                   ?dataset2 void:vocabulary ?vocabulary2.
                                   
                                   ?vocabulary1 <''' + specificity_type + '''> ?specificity.
                                   filter(?vocabulary1=?vocabulary2)
                               }
                               group by ?dataset2
                               order by desc(?similarity)
                               limit ''' + str(count) + '''
                               ''')       
                                                    
    for row in result['results']['bindings']:
        print row['dataset2']['value'], ': ', row['similarity']['value']


