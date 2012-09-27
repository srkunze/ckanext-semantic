import ckan.lib.cli
import logging

log = logging.getLogger(__name__)


class LODStatsExtCommand(cli.CkanCommand):
    '''
CKAN Example Extension

Usage::

paster example create-example-vocabs -c <path to config file>

'''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print ExampleCommand.__doc__
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'update_dataset_lodstats':
            self.create_example_vocabs()

        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def update_dataset_lodstats(self):
        print "TEST"
