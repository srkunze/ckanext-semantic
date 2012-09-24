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
    plugins.implements(plugins.IMiddleware, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

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
        map.connect('/dataset/{id}.{format}', controller='ckanext.lodstatsext.controller.lodstatsext:PackageController', action='read')

        return map
        
