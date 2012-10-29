import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.store as store


def sparql_dataset(context, data_dict):
    results = store.user.query(data_dict['query'], complete=True)
    
    if isinstance(results, str):
        return results
    
    if data_dict['objects']:
        for result in results['results']['bindings']:
            for header_name in results['head']['vars']:
                if result[header_name]['type'] == 'uri':
                    result[header_name]['object'] = h.uri_to_object(result[header_name]['value'])


    return results


def subscription_sparql_dataset(context, data_dict):
    data_dict['objects'] = False

    results = sparql_dataset({}, data_dict)

    if isinstance(results, str):
        return []
        
    return results['results']['bindings'], None

