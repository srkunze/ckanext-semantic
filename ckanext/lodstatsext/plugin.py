import os
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
        ####################################################
        #initialize lodstats table with "NO WORKING"
        ####################################################
   
        number_of_jobs = 1
        for job_index in range(number_of_jobs):
            my_pid = os.fork()
            if my_pid == 0:
                lodstatsextlib.perfom_lodstats_job()
                os._exit(0)

        return app

