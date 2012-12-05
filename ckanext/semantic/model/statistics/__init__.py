import ckan.model as model
import ckanext.semantic.model.store as store
import RDF


class StatisticsFactory(object):
    @classmethod
    def create(cls, concept):
        if concept not in StatisticsConcept.__subclasses__():
            raise Exception('Given concept is no statistics concept')
            
        statistics = concept()
        statistics.set_model(model)
        statistics.set_session(model.Session)
        statistics.set_store(store.root)
        
        return statistics


class StatisticsConcept(object):
    '''
    Abstract class for statistics concepts such as 
    dataset statistics or vocabulary statistics
    '''
    def __init__(self):
        self.results = RDF.Model()


    def set_store(self, store):
        self.store = store  


    def set_graph(self, graph):
        self.graph = graph


    def set_session(self, session):
        self.session = session


    def set_model(self, model):
        self.model = model


    def load_from_store(self):
        '''
        Load the statistics data from the store.
        Interface method supposed to be called when
        configuration of statistics instance has finished.
        Results should be stored in self.results.
        '''
        raise NotImplementedError()


    def create_results(self):
        '''
        Creates the statistics data.
        Interface method supposed to be called when
        configuration of statistics instance has finished.
        Results should be stored in self.results.
        '''
        raise NotImplementedError()


    def update_store(self):
        '''
        Update the statistical data of the store.
        Interface method supposed to be called when
        configuration of statistics instance has finished.
        Results should be stored in self.results additionally.
        '''
        raise NotImplementedError()


from dataset_statistics import DatasetStatistics
from vocabulary_statistics import VocabularyStatistics

