import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import datetime
import RDF


class SimilarityStats:
    type = {'topic': 'http://xmlns.com/foaf/0.1/topic',
            'location': 'http://www.w3.org/2003/01/geo/wgs84_pos',
            'time': 'http://www.w3.org/TR/owl-time#DateTimeDescription'
    }
    
    def __init__(self,
                 similarity_class_uri=None,
                 element_class_uri=None,
                 element_uri=None,
                 similar_element_class_uri=None,
                 graph = 'http://lodstats.org/similarities'):
        self.similarity_class_uri = similarity_class_uri
        self.element_uri = element_uri
        self.element_class_uri = element_class_uri
        self.similar_element_class_uri = similar_element_class_uri
        self.rdf = RDF.Model()
        self.rows = []
        self.graph = graph
        self.store = triplestore.ts


    def load(self, count_limit, from_store_only=False):
        if from_store_only:
            self._load_from_store_only(count_limit)
            return
            
        real = int(self.store.query('''
                                    prefix sim: <http://purl.org/ontology/similarity/>
                                    select (count(distinct ?element1) as ?count)
                                    where
                                    {
                                        ?similarity a sim:Similarity.
                                        ?similarity sim:method <''' + self.similarity_class_uri + '''>.
                                        ?similarity sim:element ?element1.
                                        ?similarity sim:element ?element2.
                                        ?element1 a <''' + self.similar_element_class_uri + '''>.
                                        filter(?element2=<''' + self.element_uri + '''> and ?element1!=?element2)
                                    }
                                    ''', single_value=True)['count']['value'])
        possible = int(self.store.query('''
                                        prefix sim: <http://purl.org/ontology/similarity/>
                                        select (count(distinct ?element) as ?count)
                                        where
                                        {
                                            ?element a <''' + self.similar_element_class_uri + '''>.
                                        }
                                        ''', single_value=True)['count']['value'])
                                        
                                        
        if float(real) / float(possible) < 0.4:
            self.update_and_commit()
        #TODO: when too old, update, too
            
        self._load_from_store_only(count_limit)


    def _load_from_store_only(self, count_limit):
        #FIXME: owl:Thing problem to determine class of element1
        #FIXME: xs:decimal(-1) necessary for virtuoso 6.1
        #TODO: take sim:distance into consideration
        rows = self.store.query('''
                                prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                prefix sim: <http://purl.org/ontology/similarity/>
                                select ?similar_element (if(bound(?weight), ?weight, (if(bound(?distance), ?distance, xs:decimal(-1)))) as ?similarity_value)
                                where
                                {
                                    ?similarity a sim:Similarity.
                                    ?similarity sim:method <''' + self.similarity_class_uri + '''>.
                                    ?similarity sim:element ?element.
                                    ?similarity sim:element ?similar_element.
                                    optional
                                    {
                                        ?similarity sim:weight ?weight.
                                    }
                                    optional
                                    {
                                        ?similarity sim:distance ?distance.
                                    }
                                    filter(?element = <''' + self.element_uri + '''> and
                                           ?element != ?similar_element)
                                }
                                order by desc(?weight) ?distance
                                limit ''' + str(count_limit) + '''
                                ''')
        
        self.rows = [(row['similar_element']['value'], row['similarity_value']['value']) for row in rows]

       
    def update_and_commit(self):
        self.update()
        self.commit()


    def update(self):
        if self.element_class_uri == 'http://rdfs.org/ns/void#Dataset':
            self._update_dataset_similarities()
        else:
            raise Exception('element_class <' + self.element_class_uri + '> not supported')
            
            
    def _update_dataset_similarities(self):
        if self.similarity_class_uri == SimilarityStats.type['topic']:
            self._update_dataset_topic_similarities()
        elif self.similarity_class_uri == SimilarityStats.type['location']:
            self._update_dataset_location_similarities()
        elif self.similarity_class_uri == SimilarityStats.type['time']:
            self._update_dataset_location_similarities()
        else:
            raise Exception('element_class <' + self.similarity_class_uri + '> for datasets not supported')


    def _update_dataset_topic_similarities(self):
        #FIXME: xs:decimal for sums necessary for virtuoso 6.1
        rows = self.store.query('''
                                prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                prefix vstats: <http://lodstats.org/vocabulary#>
                                prefix void: <http://rdfs.org/ns/void#>

                                select ?similar_dataset (sum(xs:decimal(?specificity)) as ?similarity_weight)
                                where
                                {
                                    <''' + self.element_uri + '''> void:vocabulary ?vocabulary1.
                                    ?similar_dataset void:vocabulary ?vocabulary2.
                                
                                    ?vocabulary1 vstats:cosSpecificity ?specificity.
                                    filter(?vocabulary1=?vocabulary2)
                                }
                                group by ?similar_dataset
                                order by desc(?similarity_weight)
                                ''')       

        for row in rows:
            self.append(row['similar_dataset']['value'], similarity_weight=row['similarity_weight']['value'])


    def _update_dataset_location_similarities(self):
        row0 = self.store.query('''
                                select ((?minLong+?maxLong)/2 as ?avgLong) ((?minLat+?maxLat)/2 as ?avgLat)
                                where
                                {
                                    <''' + self.element_uri + '''> void:propertyPartition ?propertyPartitionLong.
                                    ?propertyPartitionLong void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.
                                    ?propertyPartitionLong <http://rdfs.org/ns/void#minValue> ?minLong.
                                    ?propertyPartitionLong <http://rdfs.org/ns/void#maxValue> ?maxLong.

                                    <''' + self.element_uri + '''> void:propertyPartition ?propertyPartitionLat.
                                    ?propertyPartitionLat void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.
                                    ?propertyPartitionLat <http://rdfs.org/ns/void#minValue> ?minLat.
                                    ?propertyPartitionLat <http://rdfs.org/ns/void#maxValue> ?maxLat.
                                }
                                ''')[0]
        rows = self.store.query('''
                                select ?dataset ((?minLong+?maxLong)/2 as ?avgLong) ((?minLat+?maxLat)/2 as ?avgLat)
                                where
                                {
                                    ?dataset void:propertyPartition ?propertyPartitionLong.
                                    ?propertyPartitionLong void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.
                                    ?propertyPartitionLong <http://rdfs.org/ns/void#minValue> ?minLong.
                                    ?propertyPartitionLong <http://rdfs.org/ns/void#maxValue> ?maxLong.

                                    ?dataset void:propertyPartition ?propertyPartitionLat.
                                    ?propertyPartitionLat void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.
                                    ?propertyPartitionLat <http://rdfs.org/ns/void#minValue> ?minLat.
                                    ?propertyPartitionLat <http://rdfs.org/ns/void#maxValue> ?maxLat.
                                }
                                ''')       

        for row in rows:
            distance = (float(row0['avgLong']['value']) - float(row['avgLong']['value']))**2 + (float(row0['avgLat']['value']) - float(row['avgLat']['value']))**2
            self.append(row['dataset']['value'], similarity_distance=distance)
            
    
    def _update_dataset_time_similarities(self):
        pass
            
            
    def append(self, similar_element_uri, similarity_weight=None, similarity_distance=None):
        similarity_node = RDF.Node()
        self.rdf.append(RDF.Statement(similarity_node, prefix.rdf.type, prefix.sim.Similarity))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(self.element_uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(similar_element_uri)))
        if similarity_weight is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.weight, RDF.Node(literal=str(similarity_weight), datatype=prefix.xs.decimal.uri)))
        if similarity_distance is not None:
            self.rdf.append(RDF.Statement(similarity_node, prefix.sim.distance, RDF.Node(literal=str(similarity_distance), datatype=prefix.xs.decimal.uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.method, RDF.Uri(self.similarity_class_uri)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.dct.created, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))
        

    def commit(self):
        serializer = RDF.Serializer(name="ntriples")
        triples = serializer.serialize_model_to_string(self.rdf)
        print triples
        self.store.modify('''
                          delete from graph <''' + self.graph + '''>
                          {
                              ?similarity ?predicate ?object.
                          }
                          where
                          {
                              ?similarity a <http://purl.org/ontology/similarity/Similarity>.
                              ?similarity <http://purl.org/ontology/similarity/element> <''' + self.element_uri + '''>.
                              ?similarity <http://purl.org/ontology/similarity/method> <''' + self.similarity_class_uri + '''>.
                              ?similarity ?predicate ?object.
                          }
                          
                          insert in graph <''' + self.graph + '''>
                          {
                          ''' + triples + '''
                          }
                          ''')

    def clear_rdf(self):
        self.rdf = RDF.Model()

