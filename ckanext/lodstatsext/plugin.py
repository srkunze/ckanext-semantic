import ckan.model as model
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
        map.redirect('/user/recommendation', '/user/recommendation/topic')
        map.connect('/user/recommendation/{similarity_method_name}', controller='ckanext.lodstatsext.controllers.user:UserController', action='recommendation')
        map.connect('/dataset/{id}.n3', controller='ckanext.lodstatsext.controllers.package:PackageController', action='read_n3')

        return map
        
