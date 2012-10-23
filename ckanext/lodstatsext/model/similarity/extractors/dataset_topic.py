from . import EntityTopic
from . import DatasetExtractor
import ckanext.lodstatsext.model.store as store

          
class DatasetTopic(EntityTopic, DatasetExtractor):
    def _extract(self):
        rows = store.root.query('''
                                prefix void: <http://rdfs.org/ns/void#>

                                select ?dataset ?vocabulary
                                where
                                {
                                    ?dataset void:vocabulary ?vocabulary.
                                }
                                ''')

        self.entities = {}
        for row in rows:
            dataset_uri = row['dataset']['value']
            vocabulary_uri = row['vocabulary']['value']
            
            if self.entities.has_key(dataset_uri):
                self.entities[dataset_uri]['vocabularies'].append(vocabulary_uri)
            else:
                self.entities[dataset_uri] = {'vocabularies': [vocabulary_uri]}

        self._extracted = True
