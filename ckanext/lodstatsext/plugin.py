import ckan.model as model
import ckan.plugins as plugins
import logging
import logic.action as action
import lib.helpers as h
import model.similarity.similarity_stats as similarity_stats
import model.prefix as prefix
import model.similarity.methods as methods
import os

log = logging.getLogger(__name__)


class LODstatsPlugin(plugins.SingletonPlugin):
    """
    """
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    
    
    def update_config(self, config):
        here = os.path.dirname(__file__)
        template_dir = os.path.join(here, 'theme', 'templates')
        public_dir = os.path.join(here, 'theme', 'public')
        if config.get('extra_template_paths'):
            config['extra_template_paths'] += ',' + template_dir
        else:
            config['extra_template_paths'] = template_dir
        if config.get('extra_public_paths'):
            config['extra_public_paths'] += ',' + public_dir
        else:
            config['extra_public_paths'] = public_dir


    def before_map(self, map):
        map.connect('/vocabulary', controller='ckanext.lodstatsext.controllers.vocabulary:VocabularyController', action='read')

        
        map.redirect('/recommendation/', '/recommendation')
        map.connect('/recommendation', controller='ckanext.lodstatsext.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.lodstatsext.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.lodstatsext.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.lodstatsext.controllers.recommendation:RecommendationController', action='read')

        map.connect('/dataset/{id}.n3', controller='ckanext.lodstatsext.controllers.dataset:DatasetController', action='read_n3')

        return map
    
    
    def before_view(self, pkg_dict):
        #TODO: personlize that
        dataset_uri = h.dataset_to_uri(pkg_dict['name'])
        
        similarities = similarity_stats.SimilarityStats()
        similarities.set_entity(dataset_uri, str(prefix.void.Dataset))
        similarities.set_similar_entity_class(str(prefix.void.Dataset))
        similarities.set_similarity_method(methods.TopicSimilarity)
        similarities.count_limit = 5
        similarities.load()
        
        pkg_dict['similar'] = []
        for similar_entity, similarity_weight, similarity_distance in similarities.rows:
            entity_object = h.uri_to_object(similar_entity)
            if entity_object:
                pkg_dict['similar'].append(entity_object)
            
        
        
        return pkg_dict


    def get_actions(self):
        return {'subscription_sparql_dataset': action.get.subscription_sparql_dataset}

