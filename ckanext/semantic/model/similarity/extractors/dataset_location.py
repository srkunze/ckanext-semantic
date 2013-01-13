from . import EntityLocation
from . import DatasetExtractor
import ckanext.semantic.lib.location as hl
import math

          
class DatasetLocation(EntityLocation, DatasetExtractor):
    def __init__(self):
        super(DatasetLocation, self).__init__()
    

    def _extract(self, dataset_filter = ''):
        rows = self._client.query_bindings_only('''
prefix void: <http://rdfs.org/ns/void#>
prefix dstats: <http://stats.lod2.eu/vocabulary/dataset#>
prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

select ?dataset ?min_latitude ?max_latitude ?min_longitude ?max_longitude
where
{
	?dataset void:propertyPartition ?latPropertyPartition.
	?latPropertyPartition void:property geo:lat.
	?latPropertyPartition dstats:minValue ?min_latitude.
	?latPropertyPartition dstats:maxValue ?max_latitude.

	?dataset void:propertyPartition ?longPropertyPartition.
	?longPropertyPartition void:property geo:long.
	?longPropertyPartition dstats:minValue ?min_longitude.
	?longPropertyPartition dstats:maxValue ?max_longitude.

    ''' + dataset_filter + '''
}
''')

        self.entities = {}
        for row in rows:
            min_latitude = float(row['min_latitude']['value'])
            max_latitude = float(row['max_latitude']['value'])
            min_longitude = float(row['min_longitude']['value'])
            max_longitude = float(row['max_longitude']['value'])

            average_latitude = math.radians((min_latitude + max_latitude) / 2)
            average_longitude = math.radians((min_longitude + max_longitude) / 2)

            latitude_difference = math.radians(max_latitude - min_latitude)
            longitude_difference = math.radians(max_longitude - min_longitude)

            latitude_diameter = hl.earth_radius * latitude_difference
            longitude_diameter = hl.earth_radius * math.cos(average_latitude) * longitude_difference

            radius = max(latitude_diameter, longitude_diameter) / 2

            self.entities[row['dataset']['value']] = {'latitude': average_latitude,
                                                      'longitude': average_longitude,
                                                      'radius': radius}

        self._extracted = True

