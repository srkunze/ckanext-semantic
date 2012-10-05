import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import ckanext.lodstatsext.model.similarity_stats as similarity_stats
import random
import RDF


def get_datasets_similar_to_user_interest(user_uri, similarity_uri):
    result = triplestore.ts.query('''
                                prefix foaf: <http://xmlns.com/foaf/0.1/>
                                select ?dataset
                                where
                                {
                                    <''' + user_uri + '''> foaf:interest ?dataset.
                                    ?dataset a void:Dataset.
                                }
                                ''')['results']['bindings']
    random_index = random.randint(0, len(result) - 1)
    
    chosen_dataset = result[random_index]['dataset']['value']
    return similarity_stats.SimilarityStats.get_and_cache_similarities(
        similarity_uri,
        chosen_dataset,
        'http://rdfs.org/ns/void#Dataset',
        4)
