import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import datetime
import RDF


class SimilarityStats:
    def __init__(self):
        self.rdf = RDF.Model()
        
        
    def append(self, element1_uri_string, element2_uri_string, weight, method_uri_string):
        similarity_node = RDF.Node()
        self.rdf.append(RDF.Statement(similarity_node, prefix.rdf.type, prefix.sim.Similarity))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(element1_uri_string)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.element, RDF.Uri(element2_uri_string)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.weight, str(weight)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.sim.method, RDF.Uri(method_uri_string)))
        self.rdf.append(RDF.Statement(similarity_node, prefix.dct.created, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))
        

    def commit(self):
        serializer = RDF.Serializer(name="ntriples")
        triples = serializer.serialize_model_to_string(self.rdf)
        triplestore.ts.modify('''
                           delete from graph <http://lodstats.org/similarity/>
                           {
                               ?vocabulary ?predicate ?object.
                           }
                           where
                           {
                               ?vocabulary ?predicate ?object.
                           }
                           
                           insert in graph <http://lodstats.org/similarity/>
                           {
                           ''' + triples + '''
                           }
                           ''')
                           
    def load(self):
        pass        

    def clear_rdf(self):
        self.rdf = RDF.Model()

