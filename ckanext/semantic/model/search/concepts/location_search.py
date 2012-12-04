from . import SearchConcept


class LocationSearch(SearchConcept):
    def get_name(self):
        return 'location'


    def extract_filters(self, search_params):
        filters = search_params['filters']
        location = {}
        if 'location_latitude' in filters and \
           'location_longitude' in filters and \
           'location_radius' in filters:
            location['latitude'] = filters['location_latitude']
            location['longitude'] = filters['location_longitude']
            location['radius'] = filters['location_radius']
            del filters['location_latitude']
            del filters['location_longitude']
            del filters['location_radius']
        return location

    
    def build_query_dict(self, filter_):
        return {
            'select': '?min_latitude ?max_latitude ?min_longitude ?max_longitude',
            'where': '''?dataset void:propertyPartition ?latPropertyPartition.
?latPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.
?latPropertyPartition void:minValue ?min_latitude.
?latPropertyPartition void:maxValue ?max_latitude.

?dataset void:propertyPartition ?longPropertyPartition.
?longPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.
?longPropertyPartition void:minValue ?min_longitude.
?longPropertyPartition void:maxValue ?max_longitude.
''',
            }


    def post_process_results(self, results, filters):
        latitude = math.radians(float(filters['location']['latitude']))
        longitude = math.radians(float(filters['location']['longitude']))
        radius = float(filters['location']['radius']) + 1
        
        rows2 = []
        for row in rows:
            min_latitude = float(row['min_latitude']['value'])
            max_latitude = float(row['max_latitude']['value'])
            min_longitude = float(row['min_longitude']['value'])
            max_longitude = float(row['max_longitude']['value'])
            dataset_latitude = math.radians((min_latitude + max_latitude) / 2)
            dataset_longitude = math.radians((min_longitude + max_longitude) / 2)

            latitude_difference = math.radians(max_latitude - min_latitude)
            longitude_difference = math.radians(max_longitude - min_longitude)
            latitude_diameter = hl.earth_radius * latitude_difference
            longitude_diameter = hl.earth_radius * math.cos(dataset_latitude) * longitude_difference
            dataset_radius = max(latitude_diameter, longitude_diameter) / 2 + 1
            
            distance = hl.distance(latitude, longitude, dataset_latitude, dataset_longitude)

            if distance - dataset_radius <= radius:
                rows2.append(row)
        rows = rows2
