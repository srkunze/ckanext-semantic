class SearchConcept(object):
    def get_name(self):
        '''
        Return a string that identify the search concept.
        '''

    def extract_filter(self, search_params):
        '''
        Return a filter based on the search_params
        '''
        return {}


    def build_query_dict(self, filter_):
        '''
        Return a query dict that adds certain query features.
        Available is prefix, select, where, group_by.
        '''
        return {}


    def post_process_results(self, results, filters):
        '''
        Return post-processed results.
        '''
        return results


from topic_search import TopicSearch
from location_search import LocationSearch
from time_search import TimeSearch

