import ckan.model as model
import ckan.model.meta as meta
import ckanext.lodstatsext.model.lodstatsext as modelext
import datetime
import lodstats
import logging
import os
import sqlalchemy
import time

log = logging.getLogger(__name__)


def perfom_lodstats_jobs():
    ####################################################
    #initialize lodstats table with "NO WORKING"
    ####################################################
    
    job_count = 0
    desired_job_count = 1
    while True:
        time.sleep(0.1)
        if desired_job_count > job_count:
            job_count += 1
            my_pid = os.fork()
            if my_pid == 0:
                if perfom_lodstats_job() == "no update":
                    os._exit(1)
                os._exit(0)
        else:
            try:
                x, res = os.waitpid(-1, 0)
                if res == 256:
                    time.sleep(60)
                job_count -= 1
            except OSError as error:
                print error
                job_count = 0
                
    ####################################################
    # find a way to properly terminate that script
    ####################################################
    
    
def perfom_lodstats_job():
    dataset = choose_dataset()
    if dataset is None:
        return "no update"

    revision = model.repo.new_revision()
    revision.message = u'Update VoID triples'
    revision.author = u'LODStats'
    
    dataset_lodstats = get_dataset_lodstats(dataset)
    dataset_lodstats = update_dataset_lodstats(dataset, dataset_lodstats)
    model.Session.add(dataset_lodstats)

    model.repo.commit()
    
    return "updated"


def choose_dataset():
    day_4_weeks_ago = datetime.date.today() - datetime.timedelta(weeks=4)

    query = model.Session.query(model.Package)  
    query = query.outerjoin(modelext.DatasetLODStats, model.Package.id == modelext.DatasetLODStats.dataset_id)  
    query = query.filter(sqlalchemy.or_(
                            modelext.DatasetLODStats.in_progress == None,
                            sqlalchemy.and_(
                                modelext.DatasetLODStats.in_progress == False,
                                modelext.DatasetLODStats.last_evaluated < day_4_weeks_ago)))

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

    dataset_lodstats.in_progress = True
    model.Session.add(dataset_lodstats)
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
        return turn_into_error_dataset_lodstats(dataset_lodstats, 'no RDF resources available')
    

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
    
    for class_uri, result in rdf_stats.stats_results['classes']['distinct'].iteritems():
        partition = modelext.DatasetLODStatsPartition("class")
        partition.dataset_lodstats_id = dataset_lodstats.id
        partition.uri = class_uri
        partition.uri_count = result
        model.Session.add(partition)

    for base_uri, result in rdf_stats.stats_results['vocabularies'].iteritems():
        if result > 0:
            partition = modelext.DatasetLODStatsPartition("vocabulary")
            partition.dataset_lodstats_id = dataset_lodstats.id
            partition.uri = base_uri
            partition.uri_count = result
            model.Session.add(partition)

    for property_uri, result in rdf_stats.stats_results['propertiesall']['distinct'].iteritems():
        partition = modelext.DatasetLODStatsPartition("property")
        partition.dataset_lodstats_id = dataset_lodstats.id
        partition.uri = property_uri
        partition.uri_count = result
        model.Session.add(partition)

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
    
