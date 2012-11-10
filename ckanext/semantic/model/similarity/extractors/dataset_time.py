from . import EntityTime
from . import DatasetExtractor
import ckanext.semantic.model.store as store
import ckanext.semantic.lib.time as ht


class DatasetTime(EntityTime, DatasetExtractor):
    def _extract(self, dataset_filter = ''):
        rows = store.root.query('''
                                prefix void: <http://rdfs.org/ns/void#>
                                prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                
                                select ?dataset (min(?min_time) as ?min_time) ((max(?max_time)) as ?max_time)
                                where 
                                {
                                    ?dataset void:propertyPartition ?dateTimePropertyPartition.
                                    ?dateTimePropertyPartition void:minValue ?min_time.
                                    ?dateTimePropertyPartition void:maxValue ?max_time.
                                    
                                    filter(datatype(?min_time) = xs:dateTime)
                                    filter(datatype(?max_time) = xs:dateTime)
                                    
                                    ''' + dataset_filter + '''
                                }
                                group by ?dataset
                                ''')
                                
        self.entities = {}
        for row in rows:
            min_time = ht.to_naive_utc(ht.min_datetime(row['min_time']['value']))
            max_time = ht.to_naive_utc(ht.max_datetime(row['max_time']['value']))

            self.entities[row['dataset']['value']] = {'min_time': min_time, 'max_time': max_time}
        
        self._extracted = True

