import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import math
import RDF


class VocabularyStats:
    graph = 'http://lodstats.org/vocabularies'
    
    @classmethod
    def update(cls):
        result = triplestore.ts.query('''
                                   prefix void: <http://rdfs.org/ns/void#>
                                   select (count(distinct ?dataset) as ?dataset_count)
                                   where
                                   {
                                       ?dataset a void:Dataset .
                                   }
                                   ''')
        dataset_count = float(result['results']['bindings'][0]['dataset_count']['value'])
        
        result = triplestore.ts.query('''
                                   prefix void: <http://rdfs.org/ns/void#>
                                   select ?vocabulary (count(?dataset) as ?dataset_count)
                                   where
                                   {
                                       ?dataset a void:Dataset .
                                       ?dataset void:vocabulary ?vocabulary .
                                   }
                                   group by ?vocabulary
                                   order by desc(?dataset_count)
                                   ''')

                             
        vocabulary_stats = VocabularyStats()

        for row in result['results']['bindings']:
            absolute_frequency = float(row['dataset_count']['value'])
            relative_frequency = float(absolute_frequency) / float(dataset_count)
            
            vocabulary_stats.append(vocabulary_uri_string = row['vocabulary']['value'],
                                    lin_specificity = 1 - relative_frequency,
                                    cos_specificity = 0.5 * math.cos(math.pi * relative_frequency) + 0.5,
                                    log_specificity = math.log1p(1 / relative_frequency),
                                    dataset_count = int(absolute_frequency))

        vocabulary_stats.commit()


    def __init__(self):
        self.rdf = RDF.Model()
        
        
    def append(self, vocabulary_uri_string, lin_specificity, cos_specificity, log_specificity, dataset_count):
        vocabulary_uri = RDF.Uri(vocabulary_uri_string)
        
        self.rdf.append(RDF.Statement(
            vocabulary_uri,
            prefix.vstats.linSpecificity,
            RDF.Node(literal=str(lin_specificity), datatype=prefix.xs.decimal.uri)))
        self.rdf.append(RDF.Statement(
            vocabulary_uri,
            prefix.vstats.cosSpecificity,
            RDF.Node(literal=str(cos_specificity), datatype=prefix.xs.decimal.uri)))
        self.rdf.append(RDF.Statement(
            vocabulary_uri,
            prefix.vstats.logSpecificity,
            RDF.Node(literal=str(log_specificity), datatype=prefix.xs.decimal.uri)))
        self.rdf.append(RDF.Statement(
            vocabulary_uri,
            prefix.vstats.datasetCount,
            RDF.Node(literal=str(dataset_count), datatype=prefix.xs.integer.uri)))        
        
        
    def commit(self):
        serializer = RDF.Serializer(name="ntriples")
        triples = serializer.serialize_model_to_string(self.rdf)
        triplestore.ts.modify('''
                           clear graph <''' + VocabularyStats.graph + '''>
                           
                           insert in graph <''' + VocabularyStats.graph + '''>
                           {
                           ''' + triples + '''
                           }
                           ''')
                           
    def load(self):
        return triplestore.ts.query('''
                                   select *
                                   from <''' + VocabularyStats.graph + '''>
                                   where
                                   {
                                       ?vocabulary ?predicate ?object.
                                   }
                                   ''')['results']['bindings']
        

    def clear_rdf(self):
        self.rdf = RDF.Model()
