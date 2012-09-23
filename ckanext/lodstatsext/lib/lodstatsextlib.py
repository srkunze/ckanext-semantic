import os
import datetime
import lodstats
import sqlalchemy
import ckan.model as model
import ckan.model.meta as meta
import ckanext.lodstatsext.model as modelext


def perfom_lodstats_job():
    rev = model.repo.new_revision()
    
    dataset, dataset_lodstats = choose_and_lock_dataset()
    
    if dataset is None:
        return "no update"

    dataset_lodstats = update_dataset_lodstats(dataset, dataset_lodstats)
    model.Session.add(dataset_lodstats)
    model.Session.commit()
    
    rev.message = u'Update VoID/triples'
    rev.author = u'LODStats'
    model.repo.commit()
    
    return "updated"


def choose_and_lock_dataset():
    day_4_weeks_ago = datetime.date.today() - datetime.timedelta(weeks=4)

    dataset_query = model.Session.query(model.Package)
    
    query = dataset_query.outerjoin(modelext.DatasetLODStats, modelext.DatasetLODStats.dataset_id == model.Package.id)  
    query = query.filter(sqlalchemy.or_(
                            modelext.DatasetLODStats.in_progress == None,
                            sqlalchemy.and_(
                                modelext.DatasetLODStats.in_progress == False,
                                modelext.DatasetLODStats.last_evaluated < day_4_weeks_ago)))
           
           
    if query.count() == 0:
        return None, None
        
    dataset = query.first()
    
    dataset_lodstats_query = model.Session.query(modelext.DatasetLODStats)
    dataset_lodstats_query = dataset_lodstats_query.filter(modelext.DatasetLODStats.dataset_id == dataset.id)
    
    if dataset_lodstats_query.count() == 0:
        dataset_lodstats = modelext.DatasetLODStats()
        dataset_lodstats.dataset_id = dataset.id
        dataset_lodstats.in_progress = True
        model.Session.add(dataset_lodstats)
        model.Session.commit()
    else:
        dataset_lodstats = dataset_lodstats_query.one()
        dataset_lodstats.in_progress = True
        model.Session.add(dataset_lodstats)
        model.Session.commit()        
            
    return dataset, dataset_lodstats
                

"""
    rev = model.repo.new_revision()
    try:
         package_to_do.do_rdfstats()
    except ckan.exceptions.NoRDFException:
        package_to_do.rdf_last_updated = datetime.now()
        
    rev.message = u'Update VoID/triples'
    rev.author = u'RDFStats-Bot'
    model.repo.commit()
    
"""


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
    
    return dataset_lodstats
    """
    # classes
    for class_uri,result in rdfdocstats.stats_results['classes']['distinct'].iteritems():
        c = model.RDFClasses()
        c.uri = class_uri
        c.count = result
        model.Session.add(c)
        new_rdfstats.classes.append(c)
    # vocab:
    for base_uri,result in rdfdocstats.stats_results['vocabularies'].iteritems():
        if result > 0:
            v = model.RDFVocabularies()
            v.uri = base_uri
            v.count = result
            model.Session.add(v)
            new_rdfstats.vocabularies.append(v)
    # props
    for property_uri,result in rdfdocstats.stats_results['propertiesall']['distinct'].iteritems():
        p = model.RDFProperties()
        p.uri = property_uri
        p.count = result
        model.Session.add(p)
        new_rdfstats.properties.append(p)
"""


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
    
