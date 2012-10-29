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
import urllib   


log = logging.getLogger(__name__)


class SPARQLController(base.BaseController):
    def index(self):
        query = base.request.params.get('query', None)

        if not query:
            query='''select * 
where
{
   ?dataset a void:Dataset.
   ?dataset void:vocabulary <http://purl.org/ontology/bibo/>.
}
order by ?dataset
'''
        base.c.query = query

        context = {'model': model, 'session': model.Session, 'user': base.c.user}

        definition = {}
        definition['query'] = str(urllib.unquote(query))
        definition['filters'] = {}
        definition['type'] = 'sparql'
        definition['data_type'] = 'dataset'
        
        base.c.subscription = logic.get_action('subscription')(context, {'subscription_definition': definition})

        if base.c.subscription:
            results = {'head': {'vars': []},
                       'results': {'bindings': []}}
                       
            subscription_dict = {'subscription_id': base.c.subscription['id']}
            logic.get_action('subscription_item_list_update')(context, subscription_dict)
            item_list = logic.get_action('subscription_item_list')(context, subscription_dict)
            logic.get_action('subscription_mark_changes_as_seen')(context, subscription_dict)
            
            vars_ = set()
            
            for item in item_list:
                data = item['data']
                vars_.update(data.keys())
                data['__status__'] = item['status']            
                results['results']['bindings'].append(data)

            results['head']['vars'] = list(vars_)                
        else:
            results = logic.get_action('sparql_dataset')({}, {'query': query, 'objects': True})


        if isinstance(results, str):
            base.c.query_error = results
            base.c.subscriptable = False
            base.c.results = None
        else:
            base.c.query_error = None
            base.c.subscriptable = True
            base.c.results = results
    
        return base.render('sparql/index.html')

