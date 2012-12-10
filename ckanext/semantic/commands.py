import ckan.lib.cli as cli
import ckan.model as model
import lib.helpers as h
import model.prefix as prefix
import model.statistics as statistics
import datetime
import logging
import pylons

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
    summary = __doc__.split('\n')[0]
    usage = __doc__


    def command(self):
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print SemanticCommand.__doc__
            return
        self._load_config()
        getattr(self, self.args[0])(*(self.args[1:]))


    def update_dataset_due_statistics(self):
        dataset_due_statistics = statistics.StatisticsFactory.create_statistics(statistics.DatasetStatistics)
        dataset_due_statistics.set_waiting_time(pylons.config.get('ckan.semantic.waiting_time'))
        dataset_due_statistics.set_ratio_old_new(pylons.config.get('ckan.semantic.ratio_old_new'))
        dataset_due_statistics.update_store()


    def update_dataset_statistics(self, dataset_name):
        dataset_statistics = statistics.StatisticsFactory.create_statistics(statistics.DatasetStatistics)
        dataset = model.Session.query(model.Package).filter(model.Package.name == dataset_name)
        dataset_statistics.set_dataset(dataset)
        dataset_due_statistics.set_waiting_time(pylons.config.get('ckan.semantic.waiting_time'))
        dataset_due_statistics.set_ratio_old_new(pylons.config.get('ckan.semantic.ratio_old_new'))
        dataset_statistics.update_store()


    def update_vocabulary_statistics(self):
        vocabulary_statistics = statistics.StatisticsFactory.create_statistics(statistics.VocabularyStatistics)
        vocabulary_statistics.update_store()

