import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.store as store
import concepts


class Search(object):
    '''
    Performs a SPARQL search and stores the result_ids.
    '''
    def __init__(self):
        self.concepts = []
        subclasses = concepts.SearchConcept.__subclasses__()
        for subclass in subclasses:
            self.concepts.append(subclass())


    def execute(self, search_params):
        '''
        Store the results that match the filters.
        '''
        filters = self._extract_filters(search_params)
        if not filters:
            self.result_ids = []
            return
        query = self._build_query(filters)
        results = store.user.query(query)
        self.result_ids = self._post_process_results(results, filters)


    def _extract_filters(self, search_params):
        filters = {}
        for concept in self.concepts:
            filter_ =  concept.extract_filters(search_params)
            if not filter_:
                continue
            filters[concept.get_name()] = filter_
        return filters


    def _build_query(self, filters):
        query_dict = {
            'prefix': 'void: <http://rdfs.org/ns/void#>\nprefix xs: <http://www.w3.org/2001/XMLSchema#>',
            'select': '?dataset',
            'where': '?dataset a void:Dataset.',
            'group_by': '',
        }
        for concept in self.concepts:
            if concept.get_name() not in filters:
                continue
            concept_query_dict = concept.build_query_dict(filters[concept.get_name()])
            for query_part_name, query_part in concept_query_dict.iteritems():
                query_dict[query_part_name] += '\n' + query_part
        return self._compose_query_string(query_dict)


    def _compose_query_string(self, query_dict):
        if query_dict['group_by']:
            query_dict['group_by']= 'group_by %s\n' % query_dict['group_by']
        return 'prefix %s\n' % query_dict['prefix'] + \
               'select %s\n' % query_dict['select'] + \
               'where\n{%s}\n' % query_dict['where'] + \
               query_dict['group_by']


    def _post_process_results(self, results, filters):
        for concept in self.concepts:
            if concept.get_name() not in filters:
                continue
            results = concept.post_process_results(results, filters[concept.get_name()])
        return self._extract_result_ids(results)

    
    def _extract_result_ids(self, results):
        datasets = [h.uri_to_object(result['dataset']['value']) for result in results]
        dataset_ids = [dataset.id for dataset in datasets if dataset]
        return dataset_ids

