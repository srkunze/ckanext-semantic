from . import MethodData
import ckanext.semantic.model.store as store


class TopicData(MethodData):
    pass


class SpecificityWeightedTopic(TopicData):
    def __init__(self, specificity_uri):
        self.specificity_uri = specificity_uri
        rows = store.root.query('''
                                select ?vocabulary ?specificity
                                where
                                {
                                    ?vocabulary <''' + specificity_uri + '''> ?specificity.
                                }
                                ''')
        self.specificity = dict([(row['vocabulary']['value'], float(row['specificity']['value'])) for row in rows])
            
        
    def topic_weight(self, topic_uri):
        if self.specificity.has_key(topic_uri):
            return self.specificity[topic_uri]

        return 0.0
        

class EqualWeightedTopic(TopicData):
    def topic_weight(self, topic_uri):
        return 1.0

