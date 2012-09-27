import ckan.lib.cli as cli
import ckanext.lodstatsext.lib.lodstatsext as libext
import logging
import RDF
import virtuoso.virtuoso as virtuoso

log = logging.getLogger(__name__)


triplestore = virtuoso.Virtuoso("localhost", "dba", "dba", 8890, "/sparql")
graph = "http://lodstats.org/"
#print triplestore.modify('INSERT IN GRAPH <http://lodstats.org/> { <http://x.com#x> <http://x.com#y> "Juan" }')
#print triplestore.query('select * WHERE { ?s ?p ?o filter (?s = <http://x.com#x>) }', 'json')
#print triplestore.modify('delete from <http://lodstats.org/> { ?s ?p ?o } where { ?s ?p ?o filter (?s = <http://x.com#x>) }')


class LODStatsExtCommand(cli.CkanCommand):
#    summary = __doc__.split('\n')[0]  #wo kommen die denn her?
#    usage = __doc__
    summary = "Hello"
    usage = "Again"

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print ExampleCommand.__doc__
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'update_dataset_lodstats':
            self.update_dataset_lodstats()
        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def update_dataset_lodstats(self):
        dataset = libext.create_new_dataset_lodstats_revision()
        
        if dataset is None:
            return
            
        rdf_model = libext.create_rdf_model(dataset)
        serializer = RDF.Serializer(name="ntriples")
        triples = serializer.serialize_model_to_string(rdf_model)
        print triplestore.modify('delete from graph <' + graph + '> { ?dataset ?p ?o . ?o ?op ?oo . } where { ?dataset <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rdfs.org/ns/void#Dataset> . ?dataset ?p ?o. } ') 
        print triplestore.modify('insert in graph <' + graph + '> {\n' + triples + '\n} ') 

