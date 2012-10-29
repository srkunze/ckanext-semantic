import ckan.model as model
import ckan.lib.dictization as d
import ckan.plugins as plugins
import logging
import logic.action as action
import lib.helpers as h
import model.similarity.similarity_stats as similarity_stats
import model.prefix as prefix
import model.similarity.methods as methods
import model.store as store
import os

log = logging.getLogger(__name__)


class LODstatsPlugin(plugins.SingletonPlugin):
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
        filters = search_params['filters']
    
        prefix_query_string = 'prefix void: <http://rdfs.org/ns/void#>\nprefix xs: <http://www.w3.org/2001/XMLSchema#>'
        select_query_string = 'select ?dataset'
        where_query_string = 'where\n{\n    ?dataset a void:Dataset.\n'
        group_by_query_string = ''

        if 'topic' in filters:
            for topic in filters['topic']:
            #TODO: differentiate between vocabularies, classes, properties and injections
                where_query_string += '?dataset void:vocabulary <' + topic + '>.\n'
                
        if 'location' in filters:
            location = filters['location']
            where_query_string += '?dataset void:propertyPartition ?latPropertyPartition.\n'
            where_query_string += '?latPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.\n'
            where_query_string += '?latPropertyPartition void:minValue ?minLatitude.\n'
            where_query_string += '?latPropertyPartition void:maxValue ?maxLatitude.\n'
            
            where_query_string += '?dataset void:propertyPartition ?longPropertyPartition.\n'
            where_query_string += '?longPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.\n'
            where_query_string += '?longPropertyPartition void:minValue ?minLongitude.\n'
            where_query_string += '?longPropertyPartition void:maxValue ?maxLongitude.\n'

            where_query_string += 'filter(' + location['radius'] + ' + fn:max(bif:pi()*6378*(?maxLatitude - ?minLatitude)/180, 2*bif:pi()*6378*bif:cos((?maxLatitude - ?minLatitude)/2)*(?maxLongitude - ?minLongitude)/360)/2 > (2 * 3956 * bif:asin(bif:sqrt((bif:power(bif:sin(2*bif:pi() + (' + location['latitude'] + ' - (?minLatitude + ?maxLatitude)/2)*bif:pi()/360), 2) + bif:cos(2*bif:pi() + ' + location['latitude'] + '*bif:pi()/180) * bif:cos(2*bif:pi() + (?minLatitude + ?maxLatitude)/2*bif:pi()/180) * bif:power(bif:sin(2*bif:pi() + (' + location['longitude'] + ' - (?minLongitude + ?maxLongitude)/2)*bif:pi()/360), 2))))))\n'

        if 'time' in filters:
            time = filters['time']
            where_query_string += '''
                                  ?dataset void:propertyPartition ?dateTimePropertyPartition.
                                  ?dateTimePropertyPartition void:minValue ?minDateTime.
                                  ?dateTimePropertyPartition void:maxValue ?maxDateTime.
                                  filter(datatype(?minDateTime) = xs:dateTime)
                                  filter(datatype(?maxDateTime) = xs:dateTime)
                                  '''
            #virtuoso bugs make this kind of queries impossible
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
            select_query_string += ' (min(?minDateTime) as ?minDateTime) (max(?maxDateTime) as ?maxDateTime)'
            group_by_query_string = 'group by ?dataset'

        where_query_string += '}'
 
        query_string = prefix_query_string + '\n' + \
                       select_query_string + '\n' + \
                       where_query_string + '\n' + \
                       group_by_query_string + '\n'
                       
                       
        rows = store.root.query(query_string)
        
        #FIXME: workaround as long as virtuoso is not functioning properly
        if 'time' in filters:
            time = filters['time']
            [row for row in rows if row['minDateTime']['value'] != '']
            if time['type'] == 'span':
                [row for row in rows if max(row['minDateTime']['value'], time['min']) <= min(row['maxDateTime']['value'], time['max'])]
            if time['type'] == 'point':
                point = dateutil.parser.parse(time['point'])
                variance = datetime.timedelta(days=int(time['variance']))
                min_ = point - variance
                max_ = point + variance

                rows_copy = rows
                rows = []                    
                for row in rows_copy:
                    if max(row['minDateTime']['value'], min_.isoformat()) <= min(row['maxDateTime']['value'], max_.isoformat()):
                        rows.append(row)

                
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

