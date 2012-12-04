import model.store as store


class Search(object):
    '''
    Performs a SPARQL search and add additional fq parameters for SOLR.
    '''
    concepts = Search._create_concepts()
    
    def execute_search(self, search_params):
        '''
        Return a modified version of search_params according to filters.
        '''
        filters = self._extract_filters(search_params)
        if not filters:
            return search_params
            
        query = self._build_query(filters)
        results = store.user.query(query)
        result_ids = self._post_process_results(results, filters)
        search_params = self._update_search_params(search_params, result_ids)


    def _extract_filters(self, search_params):
        filters = {}
        for concept in Search.concepts:
            filters[concept.get_name()] = concept.extract_filters(search_params)
        return filters


    def _build_query(self, filters):
        query_dict = {'prefix': '', 'select': '', 'where': '', 'group_by': ''}
        for concept in Search.concepts:
            query_dict = concept.build_query_dict(filters[concept.get_name()])
            for query_part_name, query_part in query_dict.iteritems():
                query_dict[query_part_name] += query_part
        return self._compose_query_string(query_dict)


    def _compose_query_string(self, query_dict):
        return query_dict['prefix'] + '\n' + \
               query_dict['select'] + \
               query_dict['where'] + '\n' + \
               query_dict['group_by'] + '\n'


    def _post_process_results(self, results, filters):
        for concept in Search.concepts:
            results = concept.post_process_results(results, filters[concept.get_name()])
        return self._extract_result_ids(results)

    
    def _extract_result_ids(self, results):
        datasets = [h.uri_to_object(result['dataset']['value']) for result in results]
        dataset_ids = [dataset.id for dataset in datasets if dataset]
        return dataset_ids
        
        
    def _update_search_params(self, search_params, result_ids)
        for id_ in result_ids:
            search_params['fq'] += ' id:%s' % id_

        return search_params


    @classmethod
    def _create_concepts(cls):
        concepts = []
        subclasses = SearchConcept.__subclasses__()
        for subclass in subclasses:
            concepts.append(subclass())
        return concepts

