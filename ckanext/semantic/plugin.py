import ckan.model as model
import ckan.lib.dictization as d
import ckan.plugins as plugins
import logging
import logic.action as action
import lib.helpers as h
import lib.location as hl
import math
import model.similarity.similarity_stats as similarity_stats
import model.prefix as prefix
import model.similarity.methods as methods
import model.store as store
import os

log = logging.getLogger(__name__)


class SemanticPlugin(plugins.SingletonPlugin):
    """
    """
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    
    
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
        map.connect('/sparql', controller='ckanext.semantic.controllers.sparql:SPARQLController', action='index')

        map.connect('/vocabulary', controller='ckanext.semantic.controllers.vocabulary:VocabularyController', action='read')
        
        map.redirect('/recommendation/', '/recommendation')
        map.connect('/recommendation', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')
        map.connect('/recommendation/{type_}', controller='ckanext.semantic.controllers.recommendation:RecommendationController', action='read')

        map.connect('/dataset/{id}.n3', controller='ckanext.semantic.controllers.dataset:DatasetController', action='read_n3')

        return map
    
    
    def before_view(self, pkg_dict):
        #TODO: personlize that
        dataset_uri = h.dataset_to_uri(pkg_dict['name'])
        
        similarities = similarity_stats.SimilarityStats()
        similarities.set_entity(dataset_uri, str(prefix.void.Dataset))
        similarities.set_similar_entity_class(str(prefix.void.Dataset))
        #TODO: change between different similarity methods
        similarities.set_similarity_method(methods.TopicSimilarity)
        similarities.count_limit = 5
        similarities.load()
        
        pkg_dict['similar'] = []
        for similar_entity, similarity_weight, similarity_distance in similarities.rows:
            entity_object = h.uri_to_object(similar_entity)
            if entity_object:
                pkg_dict['similar'].append(entity_object)
            
        
        
        return pkg_dict
        
        
    def after_search(self, search_results, search_params):
        if 'filters' not in search_params:
            return search_results
        filters = search_params['filters']
    
        prefix_query_string = 'prefix void: <http://rdfs.org/ns/void#>\nprefix xs: <http://www.w3.org/2001/XMLSchema#>'
        select_query_string = 'select ?dataset'
        where_query_string = 'where\n{\n    ?dataset a void:Dataset.\n'
        group_by_query_string = ''

        if 'topic' in filters:
            for topic in filters['topic']:
            #TODO: differentiate between vocabularies, classes, properties and injections
                where_query_string += '?dataset void:vocabulary <' + topic + '>.\n'
                
        if 'location_latitude' in filters and \
           'location_longitude' in filters and \
           'location_radius' in filters:
            select_query_string += ' ?min_latitude ?max_latitude ?min_longitude ?max_longitude'

            where_query_string += '?dataset void:propertyPartition ?latPropertyPartition.\n'
            where_query_string += '?latPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.\n'
            where_query_string += '?latPropertyPartition void:minValue ?min_latitude.\n'
            where_query_string += '?latPropertyPartition void:maxValue ?max_latitude.\n'
            
            where_query_string += '?dataset void:propertyPartition ?longPropertyPartition.\n'
            where_query_string += '?longPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.\n'
            where_query_string += '?longPropertyPartition void:minValue ?min_longitude.\n'
            where_query_string += '?longPropertyPartition void:maxValue ?max_longitude.\n'

            #virtuoso 6 has no BIND, so debugging this formular is quite tedious and error-prone
            #where_query_string += 'filter(' + filters['location_radius'][0] + ' + fn:max(bif:pi()*6378*(?maxLatitude - ?minLatitude)/180, 2*bif:pi()*6378*bif:cos((?maxLatitude - ?minLatitude)/2)*(?maxLongitude - ?minLongitude)/360)/2 > (2 * 3956 * bif:asin(bif:sqrt((bif:power(bif:sin(2*bif:pi() + (' + filters['location_latitude'][0] + ' - (?minLatitude + ?maxLatitude)/2)*bif:pi()/360), 2) + bif:cos(2*bif:pi() + ' + filters['location_latitude'][0] + '*bif:pi()/180) * bif:cos(2*bif:pi() + (?minLatitude + ?maxLatitude)/2*bif:pi()/180) * bif:power(bif:sin(2*bif:pi() + (' + filters['location_longitude'][0] + ' - (?minLongitude + ?maxLongitude)/2)*bif:pi()/360), 2))))))\n'

        if 'time_min' in filters and 'time_max' in filters:
            where_query_string += '''
                                  ?dataset void:propertyPartition ?dateTimePropertyPartition.
                                  ?dateTimePropertyPartition void:minValue ?min_time.
                                  ?dateTimePropertyPartition void:maxValue ?max_time.
                                  filter(datatype(?min_time) = xs:dateTime)
                                  filter(datatype(?max_time) = xs:dateTime)
                                  '''
            #virtuoso 6 bugs make this kind of queries impossible
            #if self.definition['time']['type'] == 'span':
            #    where_query_string += 'filter('
            #    where_query_string += 'if(?minDateTime > "' + self.definition['time']['min'] + '"^^xs:dateTime, ?minDateTime, "' + self.definition['time']['min'] + '"^^xs:dateTime) <='
            #    where_query_string += 'if(?maxDateTime < "' + self.definition['time']['max'] + '"^^xs:dateTime, ?maxDateTime, "' + self.definition['time']['max'] + '"^^xs:dateTime)'
            #    where_query_string += ')'

            #if self.definition['time']['type'] == 'point':
            #    where_query_string += 'filter('
            #    where_query_string += 'if(?minDateTime > bif:dateadd("day", ' + self.definition['time']['variance'] + ', "' + self.definition['time']['point'] + '"^^xs:dateTime), ?minDateTime, bif:dateadd("day", ' + self.definition['time']['variance'] + ', "' + self.definition['time']['point'] + '"^^xs:dateTime)) <='
            #    where_query_string += 'if(?maxDateTime < bif:dateadd("day", ' + self.definition['time']['variance'] + ', "' + self.definition['time']['point'] + '"^^xs:dateTime), ?maxDateTime, bif:dateadd("day", ' + self.definition['time']['variance'] + ', "' + self.definition['time']['point'] + '"^^xs:dateTime))'
            #    where_query_string += ')'
            #workaround
            select_query_string += ' (min(?min_time) as ?min_time) (max(?max_time) as ?max_time)'
            group_by_query_string = 'group by ?dataset'

        where_query_string += '}'
 
        query_string = prefix_query_string + '\n' + \
                       select_query_string + '\n' + \
                       where_query_string + '\n' + \
                       group_by_query_string + '\n'
                       
                       
        rows = store.root.query(query_string)
        
        if 'location_latitude' in filters and \
           'location_longitude' in filters and \
           'location_radius' in filters:
            rows = [row for row in rows if 'min_latitude' in row]
            
            latitude = math.radians(float(filters['location_latitude'][0]))
            longitude = math.radians(float(filters['location_longitude'][0]))
            radius = float(filters['location_radius'][0]) + 1
            
            row2 = []
            
            for row in rows:
                min_latitude = float(row['min_latitude']['value'])
                max_latitude = float(row['max_latitude']['value'])
                min_longitude = float(row['min_longitude']['value'])
                max_longitude = float(row['max_longitude']['value'])
                dataset_latitude = math.radians((min_latitude + max_latitude) / 2)
                dataset_longitude = math.radians((min_longitude + max_longitude) / 2)

                latitude_difference = math.radians(max_latitude - min_latitude)
                longitude_difference = math.radians(max_longitude - min_longitude)
                latitude_diameter = hl.earth_radius * latitude_difference
                longitude_diameter = hl.earth_radius * math.cos(dataset_latitude) * longitude_difference
                dataset_radius = max(latitude_diameter, longitude_diameter) / 2 + 1
                
                distance = hl.distance(latitude, longitude, dataset_latitude, dataset_longitude)

                if distance - dataset_radius <= radius:
                    row2.append(row)

            rows = row2

        #FIXME: workaround as long as virtuoso 6 is not functioning properly
        if 'time_min' in filters and 'time_max' in filters:
            rows = [row for row in rows if 'min_time' in row]
            rows = [row for row in rows if max(row['min_time']['value'], filters['time_min'][0]) <= min(row['max_time']['value'], filters['time_max'][0])]




        datasets = [h.uri_to_object(row['dataset']['value']) for row in rows]
        datasets = [d.model_dictize.package_dictize(dataset, {'model': model}) for dataset in datasets if dataset is not None]


        combined_results =[]

        for dataset in datasets:
            for result in search_results['results']:
                if dataset['id'] != result['id']:
                    continue
                combined_results.append(result)

        search_results['results'] = combined_results
        search_results['count'] = len(combined_results)

        return search_results


    def get_actions(self):
        return {
            'sparql_dataset': action.get.sparql_dataset,
            'subscription_sparql_dataset': action.get.subscription_sparql_dataset}

