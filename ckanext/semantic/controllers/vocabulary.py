import ckan.lib.base as base
import ckanext.semantic.logic.action.get as get
import logging
import requests
import xml.dom.minidom as dom_parser
import json

log = logging.getLogger(__name__)


class VocabularyController(base.BaseController):
    def read(self, query=None):
        return get.uri_suggestions(None, {'query': query})
        
