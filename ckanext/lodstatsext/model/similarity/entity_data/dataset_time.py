import ckanext.lodstatsext.model.store as store
import datetime
import dateutil.parser


class DatasetTime(EntityTime):
    def __init__(self):
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
        
        self.entities =  dict([(row['dataset']['value'],
                                {'minTime': dateutil.parser.parse(row['minDateTime']['value']),
                                 'maxTime': dateutil.parser.parse(row['maxDateTime']['value'])}) for row in rows])
