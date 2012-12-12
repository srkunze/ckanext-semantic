from . import MethodData


class TopicData(MethodData):
    pass


class SpecificityWeightedTopic(TopicData):
    def __init__(self, specificity_uri, client):
        self.specificity_uri = specificity_uri
        rows = client.query_list('''
select ?vocabulary ?specificity
where
{
    ?vocabulary <''' + specificity_uri + '''> ?specificity.
}
''', datatypes={'vocabulary': str, 'specificity': float})

        self.specificity = dict([(row['vocabulary'], row['specificity']) for row in rows])


    def topic_weight(self, topic_uri):
        if self.specificity.has_key(topic_uri):
            return self.specificity[topic_uri]

        return 0.0
        

class EqualWeightedTopic(TopicData):
    def topic_weight(self, topic_uri):
        return 1.0

