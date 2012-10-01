import ckan.lib.cli as cli
import ckan.model as model
import ckanext.lodstatsext.model.dataset_stats as model_dataset_stats
import ckanext.lodstatsext.model.vocabulary_stats as model_vocabulary_stats
import ckanext.lodstatsext.lib.similarity_stats as lib_similarity_stats
import ckanext.lodstatsext.model.triplestore as triplestore
import ckanext.lodstatsext.model.prefix as prefix
import datetime
import logging
import RDF
import sqlalchemy


log = logging.getLogger(__name__)


class LODStatsExtCommand(cli.CkanCommand):
    '''
    CKAN Example Extension

    Usage:
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
        
        
    def test(self):
        pass
        
        
    def update_dataset_stats(self):
        model_dataset_stats.DatasetStats.update()


    def update_vocabulary_stats(self):
        model_vocabulary_stats.VocabularyStats.update()
        
    
    def update_dataset_similarities(self):
        lib_similarity_stats.update_dataset_similarities(
                    'http://localhost:5000/dataset/everything-about-water',
                    'http://lodstats.org/similarity#topic')


    def push_datasets_to_triplestore(self):
        serializer = RDF.Serializer(name='ntriples')
        
        #general data
        rdf_model = RDF.Model()
        for dataset in model.Session.query(model.Package).all():
            dataset.uri = RDF.Uri('http://localhost:5000/dataset/' + dataset.name)
            rdf_model.append(RDF.Statement(dataset.uri, prefix.owl.sameAs, RDF.Uri("urn:uuid:" + dataset.id)))
            rdf_model.append(RDF.Statement(dataset.uri, prefix.rdf.type, prefix.dcat.Dataset))
            rdf_model.append(RDF.Statement(dataset.uri, prefix.rdfs.label, dataset.name))
            rdf_model.append(RDF.Statement(dataset.uri, prefix.dct.identifier, dataset.name))
            rdf_model.append(RDF.Statement(dataset.uri, prefix.dct.title, dataset.title))
            rdf_model.append(RDF.Statement(dataset.uri, prefix.dct.description, dataset.notes))
            # + license, author, maintainer
            triples = serializer.serialize_model_to_string(rdf_model)
            triplestore.ts.modify('''
                               insert into graph <http://ckan.org/>
                               {
                               ''' + triples + '''
                               }
                               ''')

        #stats data
        rdf_model = RDF.Model()
        for dataset in model.Session.query(model.Package).all():
            dataset.uri = RDF.Uri('http://localhost:5000/dataset/' + dataset.name)
            rdf_model.append(RDF.Statement(dataset.uri, prefix.rdf.type, prefix.void.Dataset))
            rdf_model.append(RDF.Statement(dataset.uri, prefix.dstats.evaluated, 'false'))
            triples = serializer.serialize_model_to_string(rdf_model)
            triplestore.ts.modify('''
                               insert into graph <http://lodstats.org/>
                               {
                               ''' + triples + '''
                               }
                               ''')

