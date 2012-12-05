from . import StatisticsConcept
import ckanext.semantic.model.prefix as prefix
import ckanext.semantic.model.store as store
import math
import RDF


class VocabularyStatistics(StatisticsConcept):
    graph = 'http://lodstats.org/vocabularies'
    
    @classmethod
    def update(cls):
        result = store.root.query('''
                                  prefix void: <http://rdfs.org/ns/void#>
                                  select (count(distinct ?dataset) as ?dataset_count)
                                  where
                                  {
                                      ?dataset void:vocabulary ?vocabulary.
                                  }
                                  ''')
        dataset_count = float(result[0]['dataset_count']['value'])
        
        result = store.root.query('''
                                  prefix void: <http://rdfs.org/ns/void#>
                                  select ?vocabulary (count(distinct ?dataset) as ?dataset_count)
                                  where
                                  {
                                      ?dataset void:vocabulary ?vocabulary.
                                  }
                                  group by ?vocabulary
                                  order by desc(?dataset_count)
                                  ''')

        vocabulary_stats = VocabularyStats()

        for row in result:
            absolute_frequency = float(row['dataset_count']['value'])
            relative_frequency = float(absolute_frequency) / float(dataset_count)
            
            vocabulary_stats.append(vocabulary_uri = row['vocabulary']['value'],
                                    lin_specificity = 1 - relative_frequency,
                                    cos_specificity = 0.5 * math.cos(math.pi * relative_frequency) + 0.5,
                                    log_specificity = math.log1p(1 / relative_frequency),
                                    dataset_count = int(absolute_frequency))

        vocabulary_stats.commit()


    def __init__(self):
        self.rdf = RDF.Model()
        
        
    def append(self, vocabulary_uri, lin_specificity, cos_specificity, log_specificity, dataset_count):
        vocabulary_rdf_uri = RDF.Uri(vocabulary_uri)
        
        self.rdf.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.linSpecificity,
            RDF.Node(literal=str(lin_specificity), datatype=prefix.xs.decimal.uri)))
        self.rdf.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.cosSpecificity,
            RDF.Node(literal=str(cos_specificity), datatype=prefix.xs.decimal.uri)))
        self.rdf.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.logSpecificity,
            RDF.Node(literal=str(log_specificity), datatype=prefix.xs.decimal.uri)))
        self.rdf.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.datasetCount,
            RDF.Node(literal=str(dataset_count), datatype=prefix.xs.integer.uri)))        
        
        
    def commit(self):
        store.root.clear_graph(VocabularyStats.graph)
        store.root.modify(graph=VocabularyStats.graph,
                          insert_construct=h.rdf_to_string(self.rdf),
                          delete_construct='?vocabulary ?predicate ?object.\n?object ?object_predicate ?object_object.',
                          delete_where='?vocabulary ?predicate ?object.\nfilter(?vocabulary=<' + self.dataset.uri + '>)')
                           
    def load(self):
        return store.root.query('''
                                select *
                                from <''' + VocabularyStats.graph + '''>
                                where
                                {
                                    ?vocabulary ?predicate ?object.
                                }
                                ''')

