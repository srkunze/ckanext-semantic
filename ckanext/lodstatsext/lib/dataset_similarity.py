import ckan.model as model
import ckan.model.meta as meta
import ckanext.lodstatsext.model.dataset_similarity as modelext
import datetime
import lodstats
import logging
import math
import os
import RDF
import sqlalchemy
import virtuoso.virtuoso as virtuoso

log = logging.getLogger(__name__)


triplestore = virtuoso.Virtuoso("localhost", "dba", "dba", 8890, "/sparql")
graph = "http://lodstats.org/"
#print triplestore.modify('INSERT IN GRAPH <http://lodstats.org/> { <http://x.com#x> <http://x.com#y> "Juan" }')
#print triplestore.query('select * WHERE { ?s ?p ?o filter (?s = <http://x.com#x>) }', 'json')
#print triplestore.modify('delete from <http://lodstats.org/> { ?s ?p ?o } where { ?s ?p ?o filter (?s = <http://x.com#x>) }')



def update_vocabulary_specifity():
    result = triplestore.query('''
                               prefix void: <http://rdfs.org/ns/void#>
                               select (count(distinct ?dataset) as ?dataset_count)
                               from <''' + graph + '''>
                               where
                               {
                                   ?dataset a void:Dataset .
                               }
                               ''')
    dataset_count = float(result['results']['bindings'][0]['dataset_count']['value'])
    
    result = triplestore.query('''
                               prefix void: <http://rdfs.org/ns/void#>
                               select ?vocabulary (count(?dataset) as ?dataset_count)
                               from <''' + graph + '''>
                               where
                               {
                                   ?dataset a void:Dataset .
                                   ?dataset void:vocabulary ?vocabulary .
                               }
                               group by ?vocabulary
                               order by desc(?dataset_count)
                               ''')
                               
                               
    rdf_model = RDF.Model()
    ns_xs = RDF.NS("http://www.w3.org/2001/XMLSchema#")
    ns_rdf = RDF.NS("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ns_lsvs = RDF.NS("http://lodstats.org/vocabulary-specifity#")
    
    for row in result['results']['bindings']:
        vocabulary_specifity = modelext.VocabularySpecifity(row['vocabulary']['value'])
        
        vocabulary_specifity.lin_specifity = 1 - float(row['dataset_count']['value'])/float(dataset_count)
        rdf_model.append(RDF.Statement(
            RDF.Uri(vocabulary_specifity.vocabulary),
            ns_lsvs.linSpecifity,
            RDF.Node(literal=str(vocabulary_specifity.lin_specifity), datatype=ns_xs.decimal.uri)))

        vocabulary_specifity.cos_specifity = 0.5 * math.cos(math.pi * float(row['dataset_count']['value'])/float(dataset_count)) + 0.5
        rdf_model.append(RDF.Statement(
            RDF.Uri(vocabulary_specifity.vocabulary),
            ns_lsvs.cosSpecifity,
            RDF.Node(literal=str(vocabulary_specifity.cos_specifity), datatype=ns_xs.decimal.uri)))

        vocabulary_specifity.log_specifity = math.log1p(float(dataset_count)/float(row['dataset_count']['value']))
        rdf_model.append(RDF.Statement(
            RDF.Uri(vocabulary_specifity.vocabulary),
            ns_lsvs.logSpecifity,
            RDF.Node(literal=str(vocabulary_specifity.log_specifity), datatype=ns_xs.decimal.uri)))

        vocabulary_specifity.dataset_count = int(row['dataset_count']['value'])
        rdf_model.append(RDF.Statement(
            RDF.Uri(vocabulary_specifity.vocabulary),
            ns_lsvs.datasetCount,
            RDF.Node(literal=str(vocabulary_specifity.dataset_count), datatype=ns_xs.integer.uri)))

        model.Session.merge(vocabulary_specifity)   
    model.Session.commit()

    serializer = RDF.Serializer(name="ntriples")
    triples = serializer.serialize_model_to_string(rdf_model)
    triplestore.modify('''
                       delete from graph <''' + graph + '''>
                       {
                           ?vocabulary ?predicate ?object.
                       }
                       where
                       {
                           ?vocabulary ?predicate ?object.
                           filter regex(?predicate, 'http://lodstats.org/vocabulary-specifity#')
                       }
                       ''')
    triplestore.modify('''
                       insert in graph <''' + graph + '''>
                       {
                       ''' + triples + '''
                       }
                       ''')


def get_similar_datasets(dataset_url, specifity_type, count):
    result = triplestore.query('''
                               prefix lsvs: <http://lodstats.org/vocabulary-specifity#>
                               prefix void: <http://rdfs.org/ns/void#>
                               prefix xs: <http://www.w3.org/2001/XMLSchema#>
                               
                               select ?dataset2 (sum(xs:decimal(?specifity)) as ?similarity)
                               from <http://lodstats.org/>
                               where
                               {
                                   <''' + dataset_url + '''> void:vocabulary ?vocabulary1.
                                   ?dataset2 a void:Dataset.
                                   ?dataset2 void:vocabulary ?vocabulary2.
                                   
                                   ?vocabulary1 <''' + specifity_type + '''> ?specifity.
                                   filter(?vocabulary1=?vocabulary2)
                               }
                               group by ?dataset2
                               order by desc(?similarity)
                               limit ''' + str(count) + '''
                               ''')       
                                                    
    for row in result['results']['bindings']:
        print row['dataset2']['value'], ': ', row['similarity']['value']


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
