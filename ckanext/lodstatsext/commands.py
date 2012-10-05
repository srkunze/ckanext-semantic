import ckan.lib.cli as cli
import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.lib.personalization as personalization
import ckanext.lodstatsext.model.dataset_stats as model_dataset_stats
import ckanext.lodstatsext.model.vocabulary_stats as model_vocabulary_stats
import ckanext.lodstatsext.model.similarity_stats as model_similarity_stats
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
        model_similarity_stats.SimilarityStats.update_similarities(
                    'http://lodstats.org/similarity#topic',
                    h.dataset_to_uri('everything-about-water'),
                    'http://rdfs.org/ns/void#Dataset')


    def get_dataset_similarities(self):
        for row in model_similarity_stats.SimilarityStats.get_similaries(
                    'http://lodstats.org/similarity#topic',
                    'http://os.rkbexplorer.com/models/dump.tgz',
                    'http://rdfs.org/ns/void#Dataset',
                    4):
            print row[1], row[0]


    def get_and_cache_dataset_similarities(self):
        for row in model_similarity_stats.SimilarityStats.get_and_cache_similarities(
                    'http://lodstats.org/similarity#topic',
                    'http://localhost:5000/dataset/instance-hub-organizations',
                    'http://rdfs.org/ns/void#Dataset',
                    4):
            print row[1], row[0]
            
    
    def get_datasets_matching_user_interest(self):
        for row in personalization.get_datasets_similar_to_user_interest(
                                                        h.user_to_uri('meier'),
                                                        'http://lodstats.org/similarity#topic'):
            print row


    def push_datasets_to_triplestore(self):
        serializer = RDF.Serializer(name='ntriples')
        rdf_model = RDF.Model()
        for dataset in model.Session.query(model.Package).all():
            dataset.rdf_uri = RDF.Uri(h.dataset_to_uri(dataset.name))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.owl.sameAs, RDF.Uri('urn:uuid:' + dataset.id)))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.rdf.type, prefix.dcat.Dataset))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.rdfs.label, dataset.name))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.dct.identifier, dataset.name))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.dct.title, dataset.title))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.dct.description, dataset.notes))
            # + license, author, maintainer
        triples = serializer.serialize_model_to_string(rdf_model)
        triplestore.ts.modify('clear graph <http://ckan.org/datasets>')
        triplestore.ts.modify('''
                           insert into graph <http://ckan.org/datasets>
                           {
                           ''' + triples + '''
                           }
                           ''')


    def push_users_to_triplestore(self):
        serializer = RDF.Serializer(name='ntriples')
        rdf_model = RDF.Model()
        
        
        for user in model.Session.query(model.User).all():
            user.rdf_uri = RDF.Uri(h.user_to_uri(user.name))
            rdf_model.append(RDF.Statement(user.rdf_uri, prefix.owl.sameAs, RDF.Uri("urn:uuid:" + user.id)))
            rdf_model.append(RDF.Statement(user.rdf_uri, prefix.rdf.type, prefix.foaf.Person))
            
            for follow in model.Session.query(model.UserFollowingDataset).filter(model.UserFollowingDataset.follower_id == user.id).all():
                dataset = model.Session.query(model.Package).get(follow.object_id)
                dataset.rdf_uri = RDF.Uri(h.dataset_to_uri(dataset.name))
                rdf_model.append(RDF.Statement(user.rdf_uri, prefix.foaf.interest, dataset.rdf_uri))
            
            for follow in model.Session.query(model.UserFollowingUser).filter(model.UserFollowingUser.follower_id == user.id).all():
                followee = model.Session.query(model.User).get(follow.object_id)
                followee.rdf_uri = RDF.Uri(h.user_to_uri(followee.name))
                rdf_model.append(RDF.Statement(user.rdf_uri, prefix.foaf.interest, followee.rdf_uri))

        triples = serializer.serialize_model_to_string(rdf_model)
        triplestore.ts.modify('clear graph <http://ckan.org/users>')
        triplestore.ts.modify('''
                           insert into graph <http://ckan.org/users>
                           {
                           ''' + triples + '''
                           }
                           ''')

    def push_lodstats_datasets_to_triplestore(self):
        serializer = RDF.Serializer(name='ntriples')
        rdf_model = RDF.Model()
        for dataset in model.Session.query(model.Package).all():
            dataset.rdf_uri = RDF.Uri(h.dataset_to_uri(dataset.name))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.rdf.type, prefix.void.Dataset))
            rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.dstats.evaluated, 'false'))
        triples = serializer.serialize_model_to_string(rdf_model)
        triplestore.ts.modify('clear graph <http://lodstats.org/datasets>')
        triplestore.ts.modify('''
                               insert into graph <http://lodstats.org/datasets>
                               {
                               ''' + triples + '''
                               }
                               ''')

