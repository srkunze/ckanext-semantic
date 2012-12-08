from . import SearchConcept
import ckanext.semantic.lib.time as ht


class TimeSearch(SearchConcept):
    def get_name(self):
        return 'time'


    def process_filters(self, filters):
        time = {}
        if 'time_min' in filters:
            time['min'] = filters['time_min'][0]
        if 'time_max' in filters:
            time['max'] = filters['time_max'][0]
        return time

    
    def build_query_dict(self, filter_):
        return {
            'select': '(min(?min_time) as ?min_time) (max(?max_time) as ?max_time)',
            'where': '''?dataset void:propertyPartition ?dateTimePropertyPartition.
?dateTimePropertyPartition void:minValue ?min_time.
?dateTimePropertyPartition void:maxValue ?max_time.
filter(datatype(?min_time) = xs:dateTime)
filter(datatype(?max_time) = xs:dateTime)
''',
            'group_by': '?dataset',
        }


    def post_process_results(self, results, filter_):
        rows2 = []
        for row in results:
            min_time = ht.to_naive_utc(ht.min_datetime(filter_.get('time_min', '')))
            max_time = ht.to_naive_utc(ht.max_datetime(filter_.get('time_max', '')))

            dataset_min_time = ht.to_naive_utc(ht.min_datetime(row['min_time']['value']))
            dataset_max_time = ht.to_naive_utc(ht.max_datetime(row['max_time']['value']))
        
            if max(min_time, dataset_min_time) <= min(max_time, dataset_max_time):
                rows2.append(row)
        return rows2

