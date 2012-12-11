from . import StatisticsConcept
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.prefix as prefix
import math
import RDF


class VocabularyStatistics(StatisticsConcept):
    def __init__(self, client):
        super(VocabularyStatistics, self).__init__(client)
        self._client.set_graph('http://stats.lod2.eu/vocabularies')


    def create_results(self):
        dataset_count = self._get_dataset_count()
        vocabulary_counts = self._get_vocabulary_counts()
        
        self.results = RDF.Model()
        for vocabulary_count in vocabulary_counts:
            absolute_frequency = vocabulary_count['dataset_count']
            relative_frequency = absolute_frequency / dataset_count
            
            self._append(vocabulary_uri = vocabulary_count['vocabulary'],
                         absolute_frequency = absolute_frequency,
                         relative_frequency = relative_frequency,
                         complementary_frequency = 0.5 * math.cos(math.pi * relative_frequency) + 0.5,
                         inverse_frequency = math.log1p(1 / relative_frequency))


    def _get_dataset_count(self):
        return self._client.query_value('''
                                        prefix void: <http://rdfs.org/ns/void#>
                                        select (count(distinct ?dataset) as ?dataset_count)
                                        where
                                        {
                                            ?dataset void:vocabulary ?vocabulary.
                                        }
                                        ''', datatype=float)


    def _get_vocabulary_counts(self):
        return self._client.query_list('''
                                       prefix void: <http://rdfs.org/ns/void#>
                                       select ?vocabulary (count(distinct ?dataset) as ?dataset_count)
                                       where
                                       {
                                           ?dataset void:vocabulary ?vocabulary.
                                       }
                                       group by ?vocabulary
                                       order by desc(?dataset_count)
                                       ''', datatypes={'vocabulary': str, 'dataset_count': float})


    def _append(self,
                vocabulary_uri,
                absolute_frequency,
                relative_frequency,
                complementary_frequency,
                inverse_frequency):
        vocabulary_rdf_uri = RDF.Uri(vocabulary_uri)
        
        self.results.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.absoluteFrequency,
            RDF.Node(literal=str(absolute_frequency), datatype=prefix.xs.integer.uri)))
        self.results.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.relativeFrequency,
            RDF.Node(literal=str(relative_frequency), datatype=prefix.xs.decimal.uri)))
        self.results.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.complementaryFrequency,
            RDF.Node(literal=str(complementary_frequency), datatype=prefix.xs.decimal.uri)))
        self.results.append(RDF.Statement(
            vocabulary_rdf_uri,
            prefix.vstats.inverseFrequency,
            RDF.Node(literal=str(inverse_frequency), datatype=prefix.xs.decimal.uri)))        
        
        
    def update_store(self):
        self.create_results()
        self._client.clear_graph()
        self._client.modify(insert_construct=h.rdf_to_string(self.results))

