import SearchConcept from .


class TopicSearch(SearchConcept):
    def get_name(self):
        return 'topic'


    def extract_filters(self, search_param):
        topic = {}
        if 'topic' in search_param['filters']:
            topic = search_param['filters']['topic']
            del search_param['filters']['topic']
        return topic

    
    def build_query_dict(self, filter_):
        query_dict = {'where': ''}
        for topic in filter_:
            #TODO: differentiate between vocabularies, classes, properties and entities
            query_dict['where'] += '?dataset void:vocabulary <' + topic + '>.\n'
        return query_dict

