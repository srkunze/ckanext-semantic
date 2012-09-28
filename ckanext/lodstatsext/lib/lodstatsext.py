import ckan.lib.helpers as helpers
import ckan.model as model
import ckanext.lodstatsext.model.lodstatsext as modelext
import datetime
import lodstats
import logging
import sqlalchemy
import RDF


log = logging.getLogger(__name__)


def create_new_dataset_lodstats_revision():
    dataset = choose_dataset()
    if dataset is None:
        return None

    revision = model.repo.new_revision()
    revision.message = u'update'
    revision.author = u'LODStats'
    
    dataset_lodstats = get_and_lock_dataset_lodstats(dataset)
    dataset_lodstats = update_dataset_lodstats(dataset, dataset_lodstats)
    model.Session.merge(dataset_lodstats)

    model.repo.commit()
    
    return dataset


def choose_dataset():
    date_4_weeks_ago = datetime.date.today() - datetime.timedelta(weeks=4)

    query = model.Session.query(model.Package)  
    query = query.outerjoin(modelext.DatasetLODStats, model.Package.id == modelext.DatasetLODStats.dataset_id)  
    query = query.filter(sqlalchemy.or_(
                            modelext.DatasetLODStats.in_progress == None,
                            sqlalchemy.and_(
                                modelext.DatasetLODStats.in_progress == False,
                                modelext.DatasetLODStats.last_evaluated < date_4_weeks_ago)))

    if query.count() == 0:
        return None
        
    return query.first()


def get_and_lock_dataset_lodstats(dataset):
    query = model.Session.query(modelext.DatasetLODStats)
    query = query.filter(modelext.DatasetLODStats.dataset_id == dataset.id)

    if query.count() == 0:
        dataset_lodstats = modelext.DatasetLODStats()
        dataset_lodstats.dataset_id = dataset.id
    else:
        dataset_lodstats = query.one()
        query = model.Session.query(modelext.DatasetLODStatsPartition)
        query = query.filter(modelext.DatasetLODStatsPartition.dataset_lodstats_id==dataset_lodstats.id)
        for partition in query.all():
            partition.count = 0
            model.Session.merge(partition)

        
    dataset_lodstats.in_progress = True
    model.Session.merge(dataset_lodstats)
    model.Session.commit()
            
    return dataset_lodstats


def update_dataset_lodstats(dataset, dataset_lodstats):
    supported_formats = {
                            "application/x-ntriples": "nt",
                            "nt": "nt",
                            "application/x-nquads": "nq",
                            "nquads": "nq",
                            "application/rdf+xml": "rdf",
                            "rdf": "rdf",
                            "text/turtle": "ttl",
                            "rdf/turtle": "ttl",
                            "text/n3": "n3",
                            "n3": "n3",
                            "api/sparql": "sparql",
                            "sparql": "sparql"
                        }

    rdf_resource = None
    for resource in dataset.resources:
        if resource.format.lower() in supported_formats.keys():
            rdf_resource = resource
            break


    dataset_lodstats.in_progress = False
    dataset_lodstats.last_evaluated = datetime.datetime.now()


    if rdf_resource is None:
        return turn_into_error_dataset_lodstats(dataset_lodstats, 'no rdf')
    

    try:
        rdf_stats = lodstats.RDFStats(format=supported_formats[rdf_resource.format.lower()], rdfurl=rdf_resource.url)
        rdf_stats.parse()
        rdf_stats.do_stats()
    except Exception, errorstr:
        return turn_into_error_dataset_lodstats(dataset_lodstats, errorstr)


    dataset_lodstats.error = None
    dataset_lodstats.warning_count = rdf_stats.warnings
    if dataset_lodstats.warning_count > 0:
        dataset_lodstats.last_warning = unicode(rdf_stats.last_warning.message, errors='replace')

    dataset_lodstats.rdf = rdf_stats.voidify('turtle')
    dataset_lodstats.triple_count = rdf_stats.no_of_triples()
    dataset_lodstats.class_count = len(rdf_stats.stats_results['classes']['distinct'])
    dataset_lodstats.property_count = len(rdf_stats.stats_results['propertiesall']['distinct'])
    dataset_lodstats.vocabulariy_count = len(rdf_stats.stats_results['vocabularies'])
    
    partitions = [('class', uri, uri_count) for uri, uri_count in rdf_stats.stats_results['classes']['distinct'].iteritems()]
    partitions += [('vocabulary', uri, uri_count) for uri, uri_count in rdf_stats.stats_results['vocabularies'].iteritems()]
    partitions += [('property', uri, uri_count) for uri, uri_count in rdf_stats.stats_results['propertiesall']['distinct'].iteritems()]

    for type_, uri, uri_count in partitions:
        if uri_count > 0:
            query = model.Session.query(modelext.DatasetLODStatsPartition)
            query = query.filter(modelext.DatasetLODStatsPartition.type == type_)
            query = query.filter(modelext.DatasetLODStatsPartition.dataset_lodstats_id == dataset_lodstats.id)
            query = query.filter(modelext.DatasetLODStatsPartition.uri == uri)

            if query.count() == 0:
                partition = modelext.DatasetLODStatsPartition(type_)
                partition.dataset_lodstats_id = dataset_lodstats.id
                partition.uri = uri
            else:
                partition = query.one()

            partition.uri_count = uri_count
            model.Session.merge(partition)


    return dataset_lodstats


def turn_into_error_dataset_lodstats(dataset_lodstats, error_message):
    dataset_lodstats.error = error_message
    dataset_lodstats.warning_count = None
    dataset_lodstats.last_warning = None

    dataset_lodstats.rdf = None
    dataset_lodstats.triple_count = None
    dataset_lodstats.class_count = None
    dataset_lodstats.property_count = None
    dataset_lodstats.vocabulariy_count = None
        
    return dataset_lodstats


def get_dataset_lodstats(dataset):
    query = model.Session.query(modelext.DatasetLODStats)
    query = query.filter(modelext.DatasetLODStats.dataset_id == dataset.id)
    dataset_lodstats = query.one()
    
    query = model.Session.query(modelext.DatasetLODStatsPartition)
    query = query.filter(modelext.DatasetLODStatsPartition.dataset_lodstats_id == dataset_lodstats.id)
    dataset_lodstats_partitions = query.all()

    return dataset_lodstats, dataset_lodstats_partitions

    
def create_rdf_model(dataset):
    dataset_lodstats, dataset_lodstats_partitions = get_dataset_lodstats(dataset)

    rdf_model = RDF.Model()
    ns_xs = RDF.NS("http://www.w3.org/2001/XMLSchema#")
    ns_rdf = RDF.NS("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ns_rdfs = RDF.NS("http://www.w3.org/2000/01/rdf-schema#")
    ns_owl = RDF.NS("http://www.w3.org/2002/07/owl#")
    ns_void = RDF.NS("http://rdfs.org/ns/void#")
    ns_dcat = RDF.NS("http://www.w3.org/ns/dcat#")
    ns_dct = RDF.NS("http://purl.org/dc/terms/")
    ns_foaf = RDF.NS("http://xmlns.com/foaf/0.1/")
    ns_qb = RDF.NS("http://purl.org/linked-data/cube#")
    ns_stats = RDF.NS("http://example.org/XStats#")

#    url = helpers.url_for(controller='package', action='read', id=dataset.name, qualified=True)
    url = 'http://localhost:5000/dataset/' + dataset.name
    dataset.uri = RDF.Uri(url)

    rdf_model.append(RDF.Statement(dataset.uri, ns_owl.sameAs, RDF.Uri("urn:uuid:" + dataset.id)))
    rdf_model.append(RDF.Statement(dataset.uri, ns_rdf.type, ns_dcat.Dataset))
    rdf_model.append(RDF.Statement(dataset.uri, ns_rdfs.label, dataset.name))
    rdf_model.append(RDF.Statement(dataset.uri, ns_dct.identifier, dataset.name))
    rdf_model.append(RDF.Statement(dataset.uri, ns_dct.title, dataset.title))
    rdf_model.append(RDF.Statement(dataset.uri, ns_dct.description, dataset.notes))
    # + license, author, maintainer

    rdf_model.append(RDF.Statement(dataset.uri, ns_rdf.type, ns_void.Dataset))
    if dataset_lodstats.error is not None:
        return rdf_model
        
    rdf_model.append(RDF.Statement(
        dataset.uri,
        ns_void.triples,
        RDF.Node(literal=str(dataset_lodstats.triple_count), datatype=ns_xs.integer.uri)))
    rdf_model.append(RDF.Statement(
        dataset.uri,
        ns_void.classes,
        RDF.Node(literal=str(dataset_lodstats.class_count), datatype=ns_xs.integer.uri)))
    rdf_model.append(RDF.Statement(
        dataset.uri,
        ns_void.properties,
        RDF.Node(literal=str(dataset_lodstats.property_count), datatype=ns_xs.integer.uri)))
    for partition in dataset_lodstats_partitions:
        if partition.count == 0:
            continue
        if partition.type == "class":
            partition_node = RDF.Node()
            rdf_model.append(RDF.Statement(
                dataset.uri,
                ns_void["classPartition"],
                partition_node))
            rdf_model.append(RDF.Statement(
                partition_node,
                ns_void["class"],
                RDF.Uri(partition.uri)))
            rdf_model.append(RDF.Statement(
                partition_node,
                ns_void["entities"],
                RDF.Node(literal=str(partition.uri_count), datatype=ns_xs.integer.uri)))
        elif partition.type == "property":
            partition_node = RDF.Node()
            rdf_model.append(RDF.Statement(
                dataset.uri,
                ns_void["propertyPartition"],
                partition_node))
            rdf_model.append(RDF.Statement(
                partition_node,
                ns_void["property"],
                RDF.Uri(partition.uri)))
            rdf_model.append(RDF.Statement(
                partition_node,
                ns_void["triples"],
                RDF.Node(literal=str(partition.uri_count), datatype=ns_xs.integer.uri)))
        elif partition.type == "vocabulary":
            rdf_model.append(RDF.Statement(
                dataset.uri,
                ns_void["vocabulary"],
                RDF.Uri(partition.uri)))

    rdf_model.append(RDF.Statement(ns_stats.value, ns_rdf.type, ns_qb.MeasureProperty))
    rdf_model.append(RDF.Statement(ns_stats.subjectsOfType, ns_rdf.type, ns_qb.DimensonProperty))
    rdf_model.append(RDF.Statement(ns_stats.schema, ns_rdf.type, ns_qb.AttributeProperty))

    return rdf_model
    
