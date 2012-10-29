import ckan.model as model
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.prefix as prefix
import ckanext.semantic.model.dataset_stats as mds
import ckanext.semantic.model.store as store
import RDF


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

        store.root.modify(graph='http://ckan.org/datasets',
                          insert_construct=h.rdf_to_string(rdf_model),
                          delete_construct='?dataset ?predicate ?object.',
                          delete_where='?dataset ?predicate ?object.\nfilter(?dataset=<' + dataset.uri + '>)')


def triplestore_dataset_lodstats(datasets=None):
    if datasets is not None:
        for dataset in datasets:
            dataset.uri = h.dataset_to_uri(dataset.name)
            mds.DatasetStats.update(dataset.uri)
    else:
        mds.DatasetStats.update()
