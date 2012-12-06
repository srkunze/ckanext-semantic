from . import StatisticsConcept
import ckanext.semantic.model.prefix as prefix
import ckanext.semantic.model.store as store
import math
import RDF


class VocabularyStatistics(StatisticsConcept):
    def __init__(self):
        super(DatasetStatistics, self).__init__()
        self.graph = 'http://stats.lod2.eu/vocabularies'
        self.dataset = None


    def create_results(self):
        dataset_count = self._get_dataset_count()
        vocabulary_counts = self._get_vocabulary_counts()
        
        self.results = RDF.Model()
        for vocabulary_count in vocabulary_counts:
            absolute_frequency = float(row['dataset_count']['value'])
            relative_frequency = absolute_frequency / dataset_count
            
            self._append(vocabulary_uri = row['vocabulary']['value'],
                         absolute_frequency = absolute_frequency,
                         relative_frequency = relative_frequency,
                         complementary_frequency = 0.5 * math.cos(math.pi * relative_frequency) + 0.5,
                         inverse_frequency = math.log1p(1 / relative_frequency))


    def _get_dataset_count(self):
        result = store.root.query('''
                                  prefix void: <http://rdfs.org/ns/void#>
                                  select (count(distinct ?dataset) as ?dataset_count)
                                  where
                                  {
                                      ?dataset void:vocabulary ?vocabulary.
                                  }
                                  ''')
        return float(result[0]['dataset_count']['value'])


    def _get_vocabulary_counts(self):
        return = store.root.query('''
                                  prefix void: <http://rdfs.org/ns/void#>
                                  select ?vocabulary (count(distinct ?dataset) as ?dataset_count)
                                  where
                                  {
                                      ?dataset void:vocabulary ?vocabulary.
                                  }
                                  group by ?vocabulary
                                  order by desc(?dataset_count)
                                  ''')


    def _append(self,
                vocabulary_uri,
                absolute_frequency,
                relative_frequency,
                complementary_frequency,
                inverse_frequency):
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
                                from <''' + self.graph + '''>
                                where
                                {
                                    ?vocabulary ?predicate ?object.
                                }
                                ''')

