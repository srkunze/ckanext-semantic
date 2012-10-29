import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.store as store


def sparql_dataset(context, data_dict):
    results = store.user.query(data_dict['query'], complete=True)
    
    if isinstance(results, str):
        return results

    return results


def subscription_sparql_dataset(context, data_dict):
    results = sparql_dataset({}, data_dict)

    if isinstance(results, str):
        return []
        
    return results['results']['bindings'], None

