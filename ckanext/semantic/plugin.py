import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import logging
import logic.action as action
import lib.helpers as h
import model.prefix as prefix
import model.similarity.similarity as similarity
import model.similarity.extractors as extractors
import model.similarity.methods as methods
import model.search as search
import model.sparql_client as sparql_client
import os
import urllib

log = logging.getLogger(__name__)


class SemanticPlugin(plugins.SingletonPlugin):
    """
    A CKAN extension that enables CKAN to crawl RDF datasets and
    make use of the created VoID stats.
    """
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
#    plugins.implements(plugins.ISubscription, inherit=True)
    
    
    ####################################
    #   plugin.IConfigurer interface   #
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
        
        toolkit.add_resource('theme/public', 'ckanext-semantic')
        
    #   plugin.IConfigurer interface   # 
    ####################################


    ################################
    #   plugin.IRoutes interface   #               
    def before_map(self, map):
        map.connect('/sparql', controller='ckanext.semantic.controllers.sparql:SPARQLController', action='index')
        
        map.redirect('/recommendation/', '/recommendation')
        map.connect('/recommendation', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')

        map.connect('/dataset/{id}.n3', controller='ckanext.semantic.controllers.dataset:DatasetController', action='read_n3')

        return map

    #   plugin.IRoutes interface   #               
    ################################


    ###########################################
    #   plugin.IPackageController interface   #               
    def before_view(self, pkg_dict):
        if toolkit.base.c.controller == 'package':
            if toolkit.base.c.action in ['read', 'search']:
                self._add_semantic_data(pkg_dict)
            if toolkit.base.c.action in ['read']:
                self._add_similar_datasets(pkg_dict)
        return pkg_dict


    def _add_similar_datasets(self, pkg_dict):
        dataset_uri = h.dataset_to_uri(pkg_dict['name'])
        
        similarities = similarity.Similarity()
        similarities.set_entity(dataset_uri, str(prefix.void.Dataset))
        similarities.set_similar_entity_class(str(prefix.void.Dataset))
        similarities.count_limit = 5
        
        similarity_methods = {'topic': methods.TopicSimilarity,
                              'location': methods.LocationSimilarity,
                              'time': methods.TimeSimilarity}
        min_similarity_weight = {'topic': 0.1, 'location': 0.0, 'time': 0.0}
        max_similarity_distance = {'topic': 0.0, 'location': 0.3, 'time': 0.5}
        
        pkg_dict['similar'] = {}
        for method_name, method in similarity_methods.iteritems():
            similarities.set_similarity_method(method)
            similarities.min_similarity_weight = min_similarity_weight[method_name]
            similarities.max_similarity_distance = max_similarity_distance[method_name]
            similarities.load()
                        
            for similar_entity, similarity_weight, similarity_distance in similarities.rows:
                entity_object = h.uri_to_object(similar_entity)
                if not entity_object:
                    continue
                
                if method_name in pkg_dict['similar']:
                    pkg_dict['similar'][method_name].append(entity_object)
                else:
                    pkg_dict['similar'][method_name] = [entity_object]


    def _add_semantic_data(self, pkg_dict):
        dataset_uri = h.dataset_to_uri(pkg_dict['name'])
        dataset_extractors = {'topic': extractors.DatasetTopic(),
                              'location': extractors.DatasetLocation(),
                              'time': extractors.DatasetTime()}

        client = sparql_client.SPARQLClientFactory.create_client(sparql_client.VFClient, 'standard')
        for method_name, extractor in dataset_extractors.iteritems():
            extractor.set_client(client)
            extractor.extract(dataset_uri)
            if extractor.entities:
                pkg_dict[method_name] = extractor.entities.values()[0]

      
    def before_search(self, search_params):
        if 'filters' not in search_params:
            return search_params
        
        client = sparql_client.SPARQLClientFactory.create_client(sparql_client.VFClient, 'standard')
        semantic_search = search.Search(client)
        semantic_search.execute(dict(search_params['filters']))
        if semantic_search.result_ids:
            search_params['fq'] = search_params.get('fq', '') + '(id:%s' % semantic_search.result_ids[0]
            for id_ in semantic_search.result_ids[1:]:
                search_params['fq'] += ' OR id:%s' % id_
            search_params['fq'] += ')'
        elif not semantic_search.no_filters:
            search_params['fq'] = search_params.get('fq', '') + '(id=0)'

        return search_params

          
    def update_facet_titles(self, facet_titles):
        facet_titles.update({'topic': 'Topic',
                             'location_latitude': 'Latitude',
                             'location_longitude': 'Longitude',
                             'location_radius': 'Circumradius',
                             'time_min': 'Since',
                             'time_max': 'Until'})
        return facet_titles
        
    #   plugin.IPackageController interface   #
    ###########################################
    
            
    ######################################
    #   plugin.ISubscription interface   #
    def is_responsible(self, subscription_definition):
        return subscription_definition['type'] == 'sparql'
        
    
    def prepare_creation(self, subscription_definition, parameters):
        subscription_definition['query'] = parameters['query'][0]
        subscription_definition['endpoints'] = h.get_configured_endpoints_only(parameters['endpoints'])
        subscription_definition['key'] = None
        return subscription_definition


    def prepare_update(self, subscription_definition, parameters):
        subscription_definition['query'] = parameters['query'][0]
        subscription_definition['endpoints'] = h.get_configured_endpoints_only(parameters['endpoints'])
        subscription_definition['key'] = None
        return subscription_definition
        
        
    def item_data_by_definition(self, subscription_definition):
        results = logic.get_action('sparql_query')({}, {'query': subscription_definition['query'], 'endpoints': subscription_definition['endpoints']})
        if not isinstance(results, dict):
            return []
        return results['results']['bindings']


    def item_to_objects(self, subscription_item):
        datasets = []
        for key, value in subscription_item.data.iteritems():
            if value['type'] == 'uri':
                object_ = h.uri_to_object(value['value'])
                if isinstance(object_, model.Package):
                    datasets.append(object_)
        return datasets
    

    def show_url(self, subscription):
        url = base.h.url_for(controller='ckanext.semantic.controllers.sparql:SPARQLController', action='index')
        url += '?query=' + urllib.quote_plus(subscription['definition']['query'])
        return url


    def subscription_equal_definition(self, subscription, definition):
        return subscription.definition['query'] == definition['query']

    #   plugin.ISubscription interface   #
    ######################################


    #################################
    #   plugin.IActions interface   #
    def get_actions(self):
        return {
            'sparql_query': logic.side_effect_free(action.get.sparql_query),
            'uri_suggestions': logic.side_effect_free(action.get.uri_suggestions)
        }

    #   plugin.IActions interface   #
    #################################

