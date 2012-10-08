import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.triplestore as triplestore
import datetime
import dateutil.parser

class TopicWrapper:
    pass
       
           
class LocationWrapper:
    pass
       
           
class TimeWrapper:
    pass
       
           
class DatasetTopic(TopicWrapper):
    @classmethod
    def get(cls, dataset_uri):
        rows = triplestore.ts.query('''
                                    prefix void: <http://rdfs.org/ns/void#>
                                    prefix vstats: <http://lodstats.org/vocabulary#>

                                    select ?vocabulary ?vocabulary_specificity
                                    where
                                    {
                                        <''' + dataset_uri + '''> void:vocabulary ?vocabulary.
                                        ?vocabulary vstats:cosSpecificity ?vocabulary_specificity.
                                    }
                                    ''')
                                    
        return dict([(row['vocabulary']['value'], float(row['vocabulary_specificity']['value'])) for row in rows])
        
        
    @classmethod                                    
    def get_all(cls):
        rows = triplestore.ts.query('''
                                    prefix void: <http://rdfs.org/ns/void#>

                                    select ?dataset ?vocabulary
                                    where
                                    {
                                        ?dataset void:vocabulary ?vocabulary.
                                    }
                                    ''')
                                
        result = {}
        for row in rows:
            dataset_uri = row['dataset']['value']
            vocabulary_uri = row['vocabulary']['value']
            
            if result.has_key(dataset_uri):
                result[dataset_uri].append(vocabulary_uri)
            else:
                result[dataset_uri] = [vocabulary_uri]
                                
        return result


    @classmethod
    def count(cls):
        return int(triplestore.ts.query('''
                                        prefix void: <http://rdfs.org/ns/void#>

                                        select (count(distinct ?dataset) as ?count)
                                        where
                                        {
                                            ?dataset void:vocabulary ?vocabulary.
                                        }
                                        ''')[0]['count']['value'])




class DatasetLocation(LocationWrapper):
    @classmethod
    def get(cls, dataset_uri):
        row = triplestore.ts.query('''
                                   prefix void: <http://rdfs.org/ns/void#>

                                   select ?minLong ?maxLong ?minLat ?maxLat
                                   where
                                   {
                                       <''' + dataset_uri + '''> void:propertyPartition ?longPropertyPartition.
                                       ?longPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.
                                       ?longPropertyPartition void:minValue ?minLong.
                                       ?longPropertyPartition void:maxValue ?maxLong.

                                       <''' + dataset_uri + '''> void:propertyPartition ?latPropertyPartition.
                                       ?latPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.
                                       ?latPropertyPartition void:minValue ?minLat.
                                       ?latPropertyPartition void:maxValue ?maxLat.
                                   }
                                   ''')[0]
        return {'avgLong': (float(row['minLong']['value']) + float(row['maxLong']['value'])) / 2,
                'avgLat':  (float(row['minLat']['value'])  - float(row['maxLat']['value']))  / 2,
                'minLong': float(row['minLong']['value']),
                'maxLong': float(row['maxLong']['value']),
                'minLat': float(row['minLat']['value']),
                'maxLat': float(row['maxLat']['value'])}
        
    @classmethod                                    
    def get_all(cls):
        rows = triplestore.ts.query('''
                                    prefix void: <http://rdfs.org/ns/void#>

                                    select ?dataset ?minLong ?maxLong ?minLat ?maxLat
                                    where
                                    {
                                        ?dataset void:propertyPartition ?longPropertyPartition.
                                        ?longPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.
                                        ?longPropertyPartition void:minValue ?minLong.
                                        ?longPropertyPartition void:maxValue ?maxLong.

                                        ?dataset void:propertyPartition ?latPropertyPartition.
                                        ?latPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.
                                        ?latPropertyPartition void:minValue ?minLat.
                                        ?latPropertyPartition void:maxValue ?maxLat.
                                    }
                                    ''')
        
        return dict([(row['dataset']['value'],
                      {'avgLong': (float(row['minLong']['value']) + float(row['maxLong']['value'])) / 2,
                       'avgLat':  (float(row['minLat']['value'])  - float(row['maxLat']['value']))  / 2,
                       'minLong': float(row['minLong']['value']),
                       'maxLong': float(row['maxLong']['value']),
                       'minLat': float(row['minLat']['value']),
                       'maxLat': float(row['maxLat']['value'])}) for row in rows])
    

    @classmethod
    def count(cls):
        return int(triplestore.ts.query('''
                                          prefix void: <http://rdfs.org/ns/void#>

                                          select (count(distinct ?dataset) as ?count)
                                          where
                                          {
                                              ?dataset void:propertyPartition ?longPropertyPartition.
                                              ?longPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#long>.
                                              ?longPropertyPartition void:minValue ?minLong.
                                              ?longPropertyPartition void:maxValue ?maxLong.

                                              ?dataset void:propertyPartition ?latPropertyPartition.
                                              ?latPropertyPartition void:property <http://www.w3.org/2003/01/geo/wgs84_pos#lat>.
                                              ?latPropertyPartition void:minValue ?minLat.
                                              ?latPropertyPartition void:maxValue ?maxLat.
                                          }
                                          ''')[0]['count']['value'])




class DatasetTime(TimeWrapper):
    @classmethod
    def get(cls, dataset_uri):
        row = triplestore.ts.query('''
                                  prefix void: <http://rdfs.org/ns/void#>
                                  prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                
                                  select (min(?minDateTime) as ?minDateTime) ((max(?maxDateTime)) as ?maxDateTime)
                                  where 
                                  {
                                      <''' + dataset_uri + '''> void:propertyPartition ?dateTimePropertyPartition.
                                      ?dateTimePropertyPartition void:minValue ?minDateTime.
                                      ?dateTimePropertyPartition void:maxValue ?maxDateTime.
                                      filter(datatype(?maxDateTime) = xs:dateTime)
                                  }
                                  group by ?dataset
                                 ''')[0]
        return {'minTime': dateutil.parser.parse(row['minDateTime']['value']),
                'maxTime': dateutil.parser.parse(row['maxDateTime']['value'])}
        
    @classmethod                                    
    def get_all(cls):
        rows = triplestore.ts.query('''
                                  prefix void: <http://rdfs.org/ns/void#>
                                  prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                
                                  select ?dataset (min(?minDateTime) as ?minDateTime) ((max(?maxDateTime)) as ?maxDateTime)
                                  where 
                                  {
                                      ?dataset void:propertyPartition ?dateTimePropertyPartition.
                                      ?dateTimePropertyPartition void:minValue ?minDateTime.
                                      ?dateTimePropertyPartition void:maxValue ?maxDateTime.
                                      filter(datatype(?maxDateTime) = xs:dateTime)
                                  }
                                  group by ?dataset
                                  ''')
        
        return dict([(row['dataset']['value'],
                      {'minTime': dateutil.parser.parse(row['minDateTime']['value']),
                       'maxTime': dateutil.parser.parse(row['maxDateTime']['value'])}) for row in rows])

    @classmethod
    def count(cls):
        return int(triplestore.ts.query('''
                                      prefix void: <http://rdfs.org/ns/void#>
                                      prefix xs: <http://www.w3.org/2001/XMLSchema#>
                                    
                                      select (count(distinct ?dataset) as ?count)
                                      where 
                                      {
                                          ?element void:propertyPartition ?dateTimePropertyPartition.
                                          ?dateTimePropertyPartition void:minValue ?minDateTime.
                                          ?dateTimePropertyPartition void:maxValue ?maxDateTime.
                                          filter(datatype(?maxDateTime) = xs:dateTime)
                                      }
                                      group by ?element
                                      ''')[0]['count']['value'])
