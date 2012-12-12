import dateutil


class DatasetExtractor(object):
    def __init__(self):
        super(DatasetExtractor, self).__init__()
        self._evaluated_extracted = False
    
    
    def extract(self, dataset_uri):
        dataset_filter = 'filter(?dataset = <' + dataset_uri + '>)'
        self._extract(dataset_filter)


    def changed_since(self, entity_uri, oldest_update):
        if oldest_update is None:
            return True
            
        if not self._evaluated_extracted:
            self._extract_evaluated()
        
        if not self._evaluated.has_key(entity_uri):
            return False
            
        evaluated = self._evaluated[entity_uri]

        # oldest update is naive and in local time
        return evaluated.replace(tzinfo=None) - evaluated.utcoffset() > oldest_update

    
    def _extract_evaluated(self):
        rows = self._client.query_bindings_only('''
prefix dstats: <http://stats.lod2.eu/vocabulary/dataset#>
select ?dataset ?evaluated
where
{
    ?dataset dstats:evaluated ?evaluated.
}
''')

        self._evaluated = dict([(row['dataset']['value'], dateutil.parser.parse(row['evaluated']['value'])) for row in rows])
                               
        self._evaluated_extracted = True
