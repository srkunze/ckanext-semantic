import os
import time
import ckan.model as model
import ckanext.lodstatsext.lib.lodstatsextlib as lodstatsextlib
import ckan.plugins as plugins
import logging

log = logging.getLogger(__name__)


class LODstatsPlugin(plugins.SingletonPlugin):
    """
    """
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IMiddleware, inherit=True)
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
            
    def make_middleware(self, app, config):
        """
        """
        server_pid = os.fork()
        if server_pid != 0:
            return app

        ####################################################
        #initialize lodstats table with "NO WORKING"
        ####################################################
        
        job_count = 0
        desired_job_count = 1
        while True:
            time.sleep(0.1)
            if desired_job_count > job_count:
                job_count += 1
                my_pid = os.fork()
                if my_pid == 0:
                    if lodstatsextlib.perfom_lodstats_job() == "no update":
                        os._exit(1)
                    os._exit(0)
            else:
                try:
                    x, res = os.waitpid(-1, 0)
                    if res == 256:
                        time.sleep(60)
                    job_count -= 1
                except OSError as error:
                    print error
                    job_count = 0

        # unreachable path
        # find a way to terminate properly
        os._exit(0)
        
    def before_map(self, map):
        map.connect('/dataset/{id}.n3', controller='ckanext.lodstatsext.controllers.lodstatsext:PackageController', action='read_n3')

        return map
        
