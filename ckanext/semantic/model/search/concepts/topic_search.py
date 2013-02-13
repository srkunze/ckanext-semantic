from . import SearchConcept


class TopicSearch(SearchConcept):
    def get_name(self):
        return 'topic'


    def process_filters(self, filters):
        topic = {}
        if 'topic' in filters:
            topic = filters['topic']
            del filters['topic']
        return topic

    
    def build_query_dict(self, filter_):
        query_dict = {'where': ''}
        if filter_:
            query_dict['where'] += '''    ?dataset void:vocabulary ?vocabulary.
    ?dataset void:propertyPartition ?propertyPartition.
    ?propertyPartition void:property ?property.
    ?dataset void:classPartition ?classPartition.
    ?classPartition void:class ?class.

'''
        for topic in filter_:
            query_dict['where'] += '''    filter(?vocabulary=<{topic}> ||
           ?property=<{topic}> ||
           ?class=<{topic}>)'''.format(topic=topic)
        return query_dict

