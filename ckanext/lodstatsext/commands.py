import ckan.lib.cli as cli
import ckan.model as model
import ckanext.lodstatsext.lib.dataset_similarity as libext_dataset_similarity
import ckanext.lodstatsext.lib.lodstatsext as libext
import ckanext.lodstatsext.model.lodstatsext as modelext
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
    '''
    CKAN Example Extension

    Usage::

    paster example create-example-vocabs -c <path to config file>

    paster example clean -c <path to config file>
    - Remove all data created by ckanext-example

    The commands should be run from the ckanext-example directory.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__


    def command(self):
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print ExampleCommand.__doc__
            return

        cmd = self.args[0]
        self._load_config()
        getattr(self, cmd)()

        #log.error('Command "%s" not recognized' % cmd)

    def update_dataset_lodstats(self):
        '''
        Chooses a dataset, create lodstats and save them into database and triplestore.
        '''
        dataset = libext.create_new_dataset_lodstats_revision()
        if dataset is None:
            return
            
        rdf_model = libext.create_rdf_model(dataset)
        serializer = RDF.Serializer(name="ntriples")
        triples = serializer.serialize_model_to_string(rdf_model)
        uri = 'http://localhost:5000/dataset/' + dataset.name
        triplestore.modify('''
                           delete from graph <''' + graph + '''>
                           {
                               ?dataset ?p ?o.
                               ?o ?op ?oo.
                           }
                           where
                           {
                               ?dataset <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rdfs.org/ns/void#Dataset>.
                               ?dataset ?p ?o.
                               filter(?dataset=<''' + uri + '''>)
                           }
                           ''')
        triplestore.modify('''
                           insert in graph <''' + graph + '''>
                           {
                           ''' + triples + '''
                           }
                           ''') 


    def clean_up(self):
        '''
        To clean up the database in case of a server crash.
        '''
        revision = model.repo.new_revision()
        revision.message = u'clean up'
        revision.author = u'LODStats'
    
        for dataset_lodstats in model.Session.query(modelext.DatasetLODStats).all():
            dataset_lodstats.in_progress = False
            model.Session.add(dataset_lodstats)
            model.Session.commit()
            
        model.repo.commit()
    
    def update_vocabulary_specifity(self):
        '''
        Retrieves vocabulary specifity.
        '''
        libext_dataset_similarity.update_vocabulary_specifity()
        
    
    def get_similar_datasets(self):
        '''
        Retrieves vocabulary specifity.
        '''
        libext_dataset_similarity.get_similar_datasets(
            'https://commondatastorage.googleapis.com/ckannet-storage/2012-07-17T084118/hebis-00000001-05051126.rdf.gz',
            'http://lodstats.org/vocabulary-specifity#linSpecifity',
            4)
        
