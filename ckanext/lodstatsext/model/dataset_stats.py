import ckan.model as model
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
    @classmethod
    def update(cls):
        #date_4_weeks_ago = datetime.date.today() - datetime.timedelta(weeks=4)
        result = triplestore.ts.query('''
                                   prefix void: <http://rdfs.org/ns/void#>
                                   prefix dstats: <http://lodstats.org/dataset#>
                                   select ?dataset
                                   from <http://lodstats.org/>
                                   where
                                   {
                                       ?dataset a void:Dataset.
                                       ?dataset dstats:evaluated "false".
                                   }
                                   ''')
                                   
        relevant_datasets = result['results']['bindings']
        if len(relevant_datasets) == 0:
            print "no dataset requires stats update"
            return
            
        dataset_uri = relevant_datasets[0]['dataset']['value']
        dataset_stats = DatasetStats(dataset_uri)
        dataset_stats.do_stats()
        dataset_stats.commit()


    def __init__(self, dataset_uri_string):
        self.dataset = model.Session.query(model.Package).filter(('http://localhost:5000/dataset/' + model.Package.name) == dataset_uri_string).one()
        self.dataset.uri_string = dataset_uri_string
        self.dataset.uri = RDF.Uri(self.dataset.uri_string)
        self.rdf = RDF.Model()
        self.rdf_resource = None
        self.rdf_resource_format = None

        for resource in self.dataset.resources:
            if resource.format.lower() in supported_formats.keys():
                self.rdf_resource = resource
                self.rdf_resource_format = supported_formats[self.rdf_resource.format.lower()]
                break


    def do_stats(self):
        self.rdf.append(RDF.Statement(self.dataset.uri, prefix.dstats.evaluated, 'true'))
        self.rdf.append(RDF.Statement(self.dataset.uri, prefix.dstats.lastEvaluated, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))

        if self.rdf_resource is None:
            self.rdf.append(RDF.Statement(self.dataset.uri, prefix.dstats.error, prefix.dstats.NoRDFResource))
            return
        
        try:
            self.rdf_stats = lodstats.RDFStats(format=self.rdf_resource_format, rdfurl=self.rdf_resource.url)
            self.rdf_stats.parse()
            self.rdf_stats.do_stats()
            self.rdf_stats.update_model(self.dataset.uri, self.rdf)
        except Exception, errorstr:
            self.rdf.append(RDF.Statement(self.dataset.uri, prefix.dstats.error, prefix.dstats.LODStatsError))
            self.rdf.append(RDF.Statement(self.dataset.uri, prefix.dstats.errorString, errorstr))
            return
            
            
    def commit(self):
        serializer = RDF.Serializer(name='ntriples')
        triples = serializer.serialize_model_to_string(self.rdf)
            
        triplestore.ts.modify('''
                           delete from graph <http://lodstats.org/>
                           {
                               ?dataset ?p ?o.
                               ?o ?op ?oo.
                           }
                           where
                           {
                               ?dataset a <http://rdfs.org/ns/void#Dataset>.
                               ?dataset ?p ?o.
                               filter(?dataset=<''' + self.dataset.uri_string + '''>)
                           }
                           
                           insert into graph <http://lodstats.org/>
                           {
                           ''' + triples + '''
                           }
                           ''')
    
    def clear_rdf(self):
        self.rdf = RDF.Model()
