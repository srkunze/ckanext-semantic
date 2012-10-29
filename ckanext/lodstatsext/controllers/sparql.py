import ckan.lib.base as base
import ckan.lib.dictization.model_dictize as d
import ckan.logic as logic
import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.store as store
import datetime
import lodstats.stats as stats
import logging
import RDF


log = logging.getLogger(__name__)


class SPARQLController(base.BaseController):
    def index(self):
        query = base.request.params.get('query', None)


        if query:
            base.c.query = query
        else:
            base.c.query='''select * 
from <http://lodstats.org/datasets>
where
{
   ?dataset a void:Dataset.
}
order by ?dataset
'''

        results = store.user.query(base.c.query, complete=True)
        
        for result in results['results']['bindings']:
            for header_name in results['head']['vars']:
                if result[header_name]['type'] == 'uri':
                    result[header_name]['object'] = h.uri_to_object(result[header_name]['value'])

        if isinstance(results, str):
            base.c.query_error = results
            base.c.subscriptable = False
            base.c.results = None
        else:
            base.c.query_error = None
            base.c.subscriptable = True
            base.c.results = results
    
        return base.render('sparql/index.html')

