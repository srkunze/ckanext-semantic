import ckanext.semantic.model.store as store


def sparql_query(context, data_dict):
    return store.user.query(data_dict['query'], complete=True)

