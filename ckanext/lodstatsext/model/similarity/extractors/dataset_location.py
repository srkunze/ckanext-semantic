from . import EntityLocation
from . import DatasetExtractor
import ckanext.lodstatsext.model.store as store

          
class DatasetLocation(EntityLocation, DatasetExtractor):
    def __init__(self):
        super(DatasetLocation, self).__init__()
        
        
    def _extract(self):
        rows = store.root.query('''
                                prefix void: <http://rdfs.org/ns/void#>

                                select ?dataset ?minLat ?maxLat ?minLong ?maxLong
                                where
                                {
                                    ?dataset void:propertyPartition ?latPropertyPartition.
                                    ?latPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.
                                    ?latPropertyPartition void:minValue ?minLat.
                                    ?latPropertyPartition void:maxValue ?maxLat.

                                    ?dataset void:propertyPartition ?longPropertyPartition.
                                    ?longPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.
                                    ?longPropertyPartition void:minValue ?minLong.
                                    ?longPropertyPartition void:maxValue ?maxLong.
                                }
                                ''')

        self.entities = dict([(row['dataset']['value'],
                              {'avgLat': (float(row['minLat']['value']) - float(row['maxLat']['value'])) / 2,
                               'avgLong': (float(row['minLong']['value']) + float(row['maxLong']['value'])) / 2,
                               'minLat': float(row['minLat']['value']),
                               'minLong': float(row['minLong']['value']),
                               'maxLat': float(row['maxLat']['value']),
                               'maxLong': float(row['maxLong']['value'])}) for row in rows])
                               
        self._extracted = True

