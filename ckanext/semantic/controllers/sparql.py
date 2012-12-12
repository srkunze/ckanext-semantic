import ckan.lib.base as base
import ckan.lib.dictization.model_dictize as d
import ckan.logic as logic
import ckan.model as model
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.store as store
import datetime
import lodstats.stats as stats
import logging
import RDF
import pylons
import urllib   


log = logging.getLogger(__name__)


class SPARQLController(base.BaseController):
    def index(self):
        query = base.request.params.get('query', None)
        base.c.chosen_endpoints = base.request.params.getall('chosen_endpoints')

        
        base.c.available_endpoints = []
        for index in range(0, 20):
            endpoint = pylons.config.get('ckan.semantic.SPARQL_endpoint%s' % index, None)
            if endpoint:
                base.c.available_endpoints.append((endpoint, pylons.config.get('ckan.semantic.SPARQL_endpoint%s_name' % index, endpoint)))

        if not query:
            query='''
prefix void: http://rdfs.org/ns/void#

select *
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
        definition['query'] = urllib.unquote(query)
        definition['endpoints'] = base.c.chosen_endpoints
        definition['type'] = 'sparql'
        definition['data_type'] = 'dataset'
        
        try:
#            base.c.subscription = logic.get_action('subscription_show')(context, {'subscription_definition': definition})
            base.c.subscription = None
        except logic.NotAuthorized:
            pass
            
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
            results = logic.get_action('sparql_query')({}, {'query': query, 'endpoints': base.c.chosen_endpoints})
        
        if isinstance(results, str):
            base.c.query_error = results
            base.c.subscriptable = False
            base.c.results = None
        else:
            for result in results['results']['bindings']:
                for header_name in results['head']['vars']:
                    if result[header_name]['type'] == 'uri':
                        result[header_name]['object'] = h.uri_to_object(result[header_name]['value'])

            base.c.query_error = None
            base.c.subscriptable = True
            base.c.results = results
    
        return base.render('sparql/index.html')

