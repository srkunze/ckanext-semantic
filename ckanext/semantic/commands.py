import ckan.lib.cli as cli
import ckan.model as model
import lib.helpers as h
import model.update as update
import model.prefix as prefix
import model.similarity.similarity_stats as similarity_stats
import model.similarity.methods as similarity_methods
import model.vocabulary_stats as vocabulary_stats
import model.statistics as statistics
import datetime
import logging


log = logging.getLogger(__name__)


class SemanticCommand(cli.CkanCommand):
    '''
    Semantic CKAN Extension

    Usage:
        update_dataset_due_statistics
            Updates the oldest dataset statistics or
            datasets that never have had such statistics.

        update_dataset_statistics {dataset_name}
            Updates the dataset statistics of
            a dataset identified by its name.

        update_vocabulary_statistics
            Updates the vocabulary statistics.
    '''

    def command(self):
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print SemanticCommand.__doc__
            return
        self._load_config()
        getattr(self, self.args[0])(*(self.args[1:]))


    def update_dataset_due_statistics(self):
        dataset_due_statistics = statistics.Statistics.create(statistics.DatasetStatistics)
        dataset_due_statistics.update_store()


    def update_dataset_statistics(self, dataset_name):
        dataset_statistics = statistics.Statistics.create(statistics.DatasetStatistics)
        dataset = model.Session.query(model.Package).filter(model.Package.name == dataset_name)
        dataset_statistics.set_dataset(dataset)
        dataset_statistics.update_store()


    def update_vocabulary_statistics(self):
        vocabulary_statistics = statistics.Statistics.create(statistics.VocabularyStatistics)
        vocabulary_statistics.update_store()

