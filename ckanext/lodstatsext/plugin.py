import os
import time
import ckan.model as model
import ckanext.lodstatsext.lib.lodstatsextlib as lodstatsextlib

from logging import getLogger

from pylons import request
from genshi.input import HTML
from genshi.filters.transform import Transformer

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IMiddleware

log = getLogger(__name__)


class LODstatsPlugin(SingletonPlugin):
    """
    """
    implements(IMiddleware, inherit=True)

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
        desired_job_count = 3
        while True:
            time.sleep(0.1)
            if desired_job_count > job_count:
                job_count += 1
                my_pid = os.fork()
                if my_pid == 0:
                    lodstatsextlib.perfom_lodstats_job()
                    os._exit(0)
            else:
                try:
                    os.waitpid(-1, 0)
                    job_count -= 1
                except OSError as error:
                    print error
                    job_count = 0

        # unreachable path
        # find a way to terminate properly
        os._exit(0)

