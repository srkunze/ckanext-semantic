import ckanext.semantic.lib.helpers as h
import concepts


class Search(object):
    '''
    Performs a SPARQL search and stores the result_ids.
    '''
    def __init__(self, client):
        self._concepts = []
        subclasses = concepts.SearchConcept.__subclasses__()
        for subclass in subclasses:
            self._concepts.append(subclass())
        self.no_filters = True
        self.results = []
        self.result_ids = []
        self._client = client


    def execute(self, filters):
        '''
        Store the results that match the filters.
        '''
        filters = self._process_filters(filters)
        if not filters:
            self.no_filters = True
            self.results = []
            self.result_ids = []
            return
        query = self._build_query_from_filters(filters)
        self.no_filters = False
        self.results = self._client.query_bindings_only(query)
        self.result_ids = self._post_process_results(self.results, filters)


    def _process_filters(self, filters):
        new_filters = {}
        for concept in self._concepts:
            filter_ =  concept.process_filters(filters)
            if not filter_:
                continue
            new_filters[concept.get_name()] = filter_
        return new_filters


    def _build_query_from_filters(self, filters):
        query_dict = {
            'prefix': 'void: <http://rdfs.org/ns/void#>\nprefix xs: <http://www.w3.org/2001/XMLSchema#>\nprefix dstats: <http://stats.lod2.eu/vocabulary/dataset#>',
            'select': '?dataset',
            'where': '?dataset a void:Dataset.',
            'group_by': '',
        }
        for concept in self._concepts:
            if concept.get_name() not in filters:
                continue
            concept_query_dict = concept.build_query_dict(filters[concept.get_name()])
            for query_part_name, query_part in concept_query_dict.iteritems():
                query_dict[query_part_name] += '\n' + query_part
        return self._build_query_from_dict(query_dict)


    def _build_query_from_dict(self, query_dict):
        if query_dict['group_by']:
            query_dict['group_by']= 'group by %s\n' % query_dict['group_by']
        return 'prefix %s\n' % query_dict['prefix'] + \
               'select %s\n' % query_dict['select'] + \
               'where\n{%s}\n' % query_dict['where'] + \
               query_dict['group_by']


    def _post_process_results(self, results, filters):
        for concept in self._concepts:
            if concept.get_name() not in filters:
                continue
            results = concept.post_process_results(results, filters[concept.get_name()])
        return self._extract_result_ids(results)

    
    def _extract_result_ids(self, results):
        datasets = [h.uri_to_object(result['dataset']['value']) for result in results]
        dataset_ids = [dataset.id for dataset in datasets if dataset]
        return dataset_ids

