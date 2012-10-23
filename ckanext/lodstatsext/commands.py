import ckan.lib.cli as cli
import ckan.model as model
import lib.helpers as h
import model.update as update
import ckanext.lodstatsext.model.prefix as prefix
import model.similarity.similarity_stats as similarity_stats
import model.similarity.methods as similarity_methods
import model.vocabulary_stats as vocabulary_stats
import datetime
import logging
import sqlalchemy


log = logging.getLogger(__name__)


class LODStatsExtCommand(cli.CkanCommand):
    '''
    CKAN LODStats Extension

    Usage:
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__


    def command(self):
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print ExampleCommand.__doc__
            return
            

        self._load_config()
        getattr(self, self.args[0])(*(self.args[1:]))


    def test(self):
        pass
        

    def update(self, class_='dataset', name=None):
        if class_ == 'dataset':
            query = model.Session.query(model.Package)
            if name is not None:
                query = query.filter(model.Package.name == name)
            update.triplestore_dataset(query.all())

        if class_ == 'lodstats':
            if name == 'due':
                update.triplestore_dataset_lodstats()
            else:
                query = model.Session.query(model.Package)
                if name is not None:
                    query = query.filter(model.Package.name == name)
                update.triplestore_dataset_lodstats(query.all())


    def update_vocabulary_stats(self):
        vocabulary_stats.VocabularyStats.update()
        
    
    def similarity_stats(self,
                         method,
                         similarity_method_name,
                         entity_name,
                         user_name,
                         entity_type='dataset',
                         min_weight=None,
                         max_distance=None,
                         similar_entity_type='dataset'):
                         
        similarity_method_class = {'topic': similarity_methods.TopicSimilarity,
                                   'location': similarity_methods.LocationSimilarity,
                                   'time': similarity_methods.TimeSimilarity,
                                  }[similarity_method_name]

        entity_uri = {'dataset': h.dataset_to_uri(entity_name),
                      'subscription': h.subscription_to_uri(user_name, entity_name)}[entity_type]
        entity_class_uri = {'dataset': str(prefix.void.Dataset.uri),
                            'subscription': str(prefix.ckan.Subscription.uri)}[entity_type]
        similar_entity_class_uri = {'dataset': str(prefix.void.Dataset.uri),
                                    'subscription': str(prefix.ckan.Subscription.uri)}[similar_entity_type]

         
        similarities = similarity_stats.SimilarityStats()
        similarities.set_entity(entity_uri, entity_class_uri)
        similarities.set_similar_entity_class(similar_entity_class_uri)
        similarities.set_similarity_method(similarity_method_class)
        similarities.count_limit = 5
        similarities.min_similarity_distance = min_weight
        similarities.max_similarity_weight = max_distance

        if method == 'update':
            similarities.update()
            
        if method == 'load1':
            similarities.load()
            for row in similarities.rows:
                print row
                
        if method == 'load2':
            similarities.load(update_when_necessary=False)
            for row in similarities.rows:
                print row

