from . import SearchConcept


class TopicSearch(SearchConcept):
    def get_name(self):
        return 'topic'


    def extract_filter(self, search_params):
        filters = search_params['filters']
        topic = {}
        if 'topic' in filters:
            topic = filters['topic']
            del filters['topic']
        return topic

    
    def build_query_dict(self, filter_):
        query_dict = {'where': ''}
        for topic in filter_:
            #TODO: differentiate between vocabularies, classes, properties and entities
            query_dict['where'] += '?dataset void:vocabulary <' + topic + '>.\n'
        return query_dict

