from . import EntityTime
from . import DatasetExtractor
import ckanext.lodstatsext.model.store as store
import datetime
import dateutil.parser


class DatasetTime(EntityTime, DatasetExtractor):
    def _extract(self):
        rows = store.root.query('''
                                prefix void: <http://rdfs.org/ns/void#>
                                prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                
                                select ?dataset (min(?minDateTime) as ?minDateTime) ((max(?maxDateTime)) as ?maxDateTime)
                                where 
                                {
                                    ?dataset void:propertyPartition ?dateTimePropertyPartition.
                                    ?dateTimePropertyPartition void:minValue ?minDateTime.
                                    ?dateTimePropertyPartition void:maxValue ?maxDateTime.
                                    filter(datatype(?minDateTime) = xs:dateTime)
                                    filter(datatype(?maxDateTime) = xs:dateTime)
                                }
                                group by ?dataset
                                ''')
                                
        self.entities = {}
        for row in rows:
            minTime = dateutil.parser.parse(row['minDateTime']['value'])
            maxTime = dateutil.parser.parse(row['maxDateTime']['value'])

            minTime = minTime.replace(tzinfo=None) - minTime.utcoffset()
            maxTime = maxTime.replace(tzinfo=None) - maxTime.utcoffset()

            self.entities[row['dataset']['value']] = {'minTime': minTime, 'maxTime': maxTime}
        
        self._extracted = True

