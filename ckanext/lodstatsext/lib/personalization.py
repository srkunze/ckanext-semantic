import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import ckanext.lodstatsext.model.similarity_stats as mss
import random
import RDF


def entities_similar_to_user_interest(user_uri,
                                      similarity_method,
                                      entity_class_uri,
                                      similar_entity_class_uri):
    rows = triplestore.ts.query('''
                                prefix foaf: <http://xmlns.com/foaf/0.1/>
                                select ?entity
                                where
                                {
                                    <''' + user_uri + '''> foaf:interest ?entity.
                                    ?entity a <''' + entity_class_uri + '''>.
                                }
                                ''')
    random_index = random.randint(0, len(rows) - 1)
    
    chosen_entity_uri = rows[random_index]['entity']['value']

                                    
    similarities = mss.SimilarityStats(similarity_method,
                                       chosen_entity_uri,
                                       entity_class_uri,
                                       similar_entity_class_uri)
    similarities.load(4)
    
    return similarities.rows
    
