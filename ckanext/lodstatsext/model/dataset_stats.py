import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import datetime
import lodstats
import RDF
import sqlalchemy


supported_formats = {
    'application/x-ntriples': 'nt',
    'nt': 'nt',
    'application/x-nquads': 'nq',
    'nquads': 'nq',
    'application/rdf+xml': 'rdf',
    'rdf': 'rdf',
    'text/turtle': 'ttl',
    'rdf/turtle': 'ttl',
    'text/n3': 'n3',
    'n3': 'n3',
    'api/sparql': 'sparql',
    'sparql': 'sparql'
}


class DatasetStats:
    graph = 'http://lodstats.org/datasets'
    
    @classmethod
    def update(cls, dataset_uri=None):
        if dataset_uri is None:
            #TODO: when too old, update, too
            #date_4_weeks_ago = datetime.date.today() - datetime.timedelta(weeks=4)
            relevant_datasets = triplestore.ts.query('''
                                       prefix void: <http://rdfs.org/ns/void#>
                                       prefix dstats: <http://lodstats.org/dataset#>
                                       select ?dataset
                                       from <''' + DatasetStats.graph + '''>
                                       where
                                       {
                                           ?dataset a void:Dataset.
                                           ?dataset dstats:evaluated "false".
                                       }
                                       ''')

            if len(relevant_datasets) == 0:
                print "no dataset requires stats update"
                return
                
            dataset_uri = relevant_datasets[0]['dataset']['value']


        dataset_stats = DatasetStats(dataset_uri)
        dataset_stats.do_stats()
        dataset_stats.commit()


    def __init__(self, dataset_uri):
        self.dataset = h.uri_to_db_object(dataset_uri)
        self.dataset.uri = dataset_uri
        self.rdf = RDF.Model()
        self.rdf_resource = None
        self.rdf_resource_format = None

        for resource in self.dataset.resources:
            if resource.format.lower() in supported_formats.keys():
                self.rdf_resource = resource
                self.rdf_resource_format = supported_formats[self.rdf_resource.format.lower()]
                break


    def do_stats(self):
        dataset_rdf_uri = RDF.Uri(self.dataset.uri)
        self.rdf.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.evaluated, 'true'))
        self.rdf.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.lastEvaluated, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))

        if self.rdf_resource is None:
            self.rdf.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.error, prefix.dstats.NoRDFResource))
            return

        try:
            self.rdf_stats = lodstats.RDFStats(format=self.rdf_resource_format, rdfurl=self.rdf_resource.url)
            self.rdf_stats.parse()
            self.rdf_stats.do_stats()
            self.rdf_stats.update_model(dataset_rdf_uri, self.rdf)
        except Exception as errorstr:
            self.rdf.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.error, prefix.dstats.LODStatsError))
            if isinstance(errorstr, Exception):
                self.rdf.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.errorString, RDF.Node(literal=errorstr.message, datatype=prefix.xs.string.uri)))
            else:
                self.rdf.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.errorString, RDF.Node(literal=errorstr, datatype=prefix.xs.string.uri)))
            return
            
            
    def commit(self):
        serializer = RDF.Serializer(name='ntriples')
        triples = serializer.serialize_model_to_string(self.rdf)
        triplestore.ts.modify('''
                           delete from graph <''' + DatasetStats.graph + '''>
                           {
                               ?dataset ?predicate ?object.
                               ?object ?object_predicate ?object_object.
                           }
                           where
                           {
                               ?dataset ?predicate ?object.
                               filter(?dataset=<''' + self.dataset.uri + '''>)
                           }
                           
                           insert into graph <''' + DatasetStats.graph + '''>
                           {
                           ''' + triples + '''
                           }
                           ''')
    
    def clear_rdf(self):
        self.rdf = RDF.Model()
