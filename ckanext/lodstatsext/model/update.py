import ckan.model as model
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.dataset_stats as mds
import ckanext.lodstatsext.model.store as store
import RDF


def triplestore_user(users):
    for user in users:
        user.uri = h.user_to_uri(user.name)
        user.rdf_uri = RDF.Uri(user.uri)

        rdf_model = RDF.Model()
        rdf_model.append(RDF.Statement(user.rdf_uri, prefix.owl.sameAs, RDF.Uri("urn:uuid:" + user.id)))
        rdf_model.append(RDF.Statement(user.rdf_uri, prefix.rdf.type, prefix.foaf.Person))
        
        for follow in model.Session.query(model.UserFollowingDataset).filter(model.UserFollowingDataset.follower_id == user.id).all():
            dataset = model.Session.query(model.Package).get(follow.object_id)
            dataset.rdf_uri = RDF.Uri(h.dataset_to_uri(dataset.name))
            rdf_model.append(RDF.Statement(user.rdf_uri, prefix.foaf.interest, dataset.rdf_uri))
        
        for follow in model.Session.query(model.UserFollowingUser).filter(model.UserFollowingUser.follower_id == user.id).all():
            followee = model.Session.query(model.User).get(follow.object_id)
            followee.rdf_uri = RDF.Uri(h.user_to_uri(followee.name))
            rdf_model.append(RDF.Statement(user.rdf_uri, prefix.foaf.interest, followee.rdf_uri))

        store.root.modify('http://ckan.org/users',
                          h.rdf_to_string(rdf_model),
                          '?user ?predicate ?object.',
                          '?user ?predicate ?object.\nfilter(?user=<' + user.uri + '>)')


def triplestore_dataset(datasets):
    for dataset in datasets:
        dataset.uri = h.dataset_to_uri(dataset.name)
        dataset.rdf_uri = RDF.Uri(dataset.uri)

        rdf_model = RDF.Model()
        rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.owl.sameAs, RDF.Uri('urn:uuid:' + dataset.id)))
        rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.rdf.type, prefix.dcat.Dataset))
        rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.rdfs.label, dataset.name))
        rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.dct.identifier, dataset.name))
        rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.dct.title, dataset.title))
        rdf_model.append(RDF.Statement(dataset.rdf_uri, prefix.dct.description, dataset.notes))
        # + license, author, maintainer

        store.root.modify('http://ckan.org/datasets',
                          h.rdf_to_string(rdf_model),
                          '?dataset ?predicate ?object.',
                          '?dataset ?predicate ?object.\nfilter(?dataset=<' + dataset.uri + '>)')


def triplestore_dataset_lodstats(datasets=None):
    if datasets is not None:
        for dataset in datasets:
            dataset.uri = h.dataset_to_uri(dataset.name)
            mds.DatasetStats.update(dataset.uri)
    else:
        mds.DatasetStats.update()
