import ckan.model as model
import ckanext.lodstatsext.lib.dataset_similarity as dataset_similarity_lib
import ckanext.lodstatsext.lib.lodstatsext as lodstatsext_lib
import ckan.plugins as plugins
import logging
import os

log = logging.getLogger(__name__)


class LODstatsPlugin(plugins.SingletonPlugin):
    """
    """
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    
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
        map.connect('/dataset/{id}.n3', controller='ckanext.lodstatsext.controllers.lodstatsext:PackageController', action='read_n3')

        return map
        
