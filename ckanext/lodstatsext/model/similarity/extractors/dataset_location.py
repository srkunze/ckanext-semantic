from . import EntityLocation
from . import DatasetExtractor
import ckanext.lodstatsext.model.store as store
import math

          
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
        self.entities = {}
        for row in rows:
            min_latitude = float(row['minLat']['value'])
            max_latitude = float(row['maxLat']['value'])
            min_longitude = float(row['minLong']['value'])
            max_longitude = float(row['maxLong']['value'])

            average_latitude = math.radians((min_latitude + max_latitude) / 2)
            average_longitude = math.radians((min_longitude + max_longitude) / 2)

            latitude_difference = math.radians(max_latitude - min_latitude)
            longitude_difference = math.radians(max_longitude - min_longitude)

            earth_radius = 6378
            latitude_diameter = earth_radius * latitude_difference
            longitude_diameter = earth_radius * math.cos(average_latitude) * longitude_difference

            radius = max(latitude_diameter, longitude_diameter) / 2

            self.entities[row['dataset']['value']] = {'latitude': average_latitude,
                                                      'longitude': average_longitude,
                                                      'radius': radius}

        self._extracted = True

