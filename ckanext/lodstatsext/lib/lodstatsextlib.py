import os
import datetime
import lodstats
import sqlalchemy
import time
import ckan.model as model
import ckan.model.meta as meta
import ckanext.lodstatsext.model as modelext


def perfom_lodstats_job():
    while True:
        time.sleep(1)
        dataset = choose_dataset()
        perform_lodstats(dataset)


def choose_dataset():
    day_4_weeks_ago = datetime.date.today() - datetime.timedelta(weeks=4)

    dataset_query = model.Session.query(model.Package)
    
    query = dataset_query.outerjoin(modelext.DatasetLODStats, modelext.DatasetLODStats.dataset_id == model.Package.id)  
    query = query.filter(sqlalchemy.or_(
                            modelext.DatasetLODStats.last_evaluated == None,
                            sqlalchemy.and_(
                                modelext.DatasetLODStats.processing == False,
                                modelext.DatasetLODStats.last_evaluated < day_4_weeks_ago)))
    return query.first()
                

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


def perform_lodstats(dataset):
    rdfish_resources = []
    # find RDF-ish resources
    rdfish_resource = None
    class BreakIt:
        pass

    try:
        for resource in dataset.resources:
            if resource.format.lower() in ["application/x-ntriples", "nt"]:
                rdfish_resource = ("nt", resource.url)
                raise BreakIt
        for resource in dataset.resources:
            if resource.format.lower() in ["application/x-nquads", "nquads"]:
                rdfish_resource = ("nq", resource.url)
                raise BreakIt
        for resource in dataset.resources:
            if resource.format.lower() in ["application/rdf+xml", "rdf"]:
                rdfish_resource = ("rdf", resource.url)
                raise BreakIt
        for resource in dataset.resources:
            if resource.format.lower() in ["text/turtle", "rdf/turtle", "ttl"]:
                rdfish_resource = ("ttl", resource.url)
                raise BreakIt
        for resource in dataset.resources:
            if resource.format.lower() in ["text/n3", "n3"]:
                rdfish_resource = ("n3", resource.url)
                raise BreakIt
        for resource in dataset.resources:
            if resource.format.lower() in ["api/sparql", "sparql"]:
                rdfish_resource = ("sparql", resource.url)
    except BreakIt:
        pass


    error = None
 
    dataset_lodstats = modelext.DatasetLODStats()
    dataset_lodstats.dataset_id = dataset.id
    dataset_in_progress
    model.Session.add(dataset_lodstats)
   
    if rdfish_resource is None:
        error = 'no RDF-ish resources available'
        create_error_stats()
        return
        
    try:
        rdfdocstats = lodstats.RDFStats(format=rdfish_resource[1], rdfurl=rdfish_resource[0])
        rdfdocstats.parse(callback_fun)
        rdfdocstats.do_stats(callback_fun)
    except Exception, errorstr:
        error = errorstr
        print error

    if error is None:
        self.triples = rdfdocstats.no_of_triples()
        new_rdfstats.triples  = rdfdocstats.no_of_triples()
        new_rdfstats.void = rdfdocstats.voidify('turtle')
        new_rdfstats.warnings = rdfdocstats.warnings
        if rdfdocstats.warnings > 0:
            new_rdfstats.rdf_last_warning = unicode(rdfdocstats.last_warning.message, errors='replace')
        new_rdfstats.error = None
        new_rdfstats.no_of_classes = len(rdfdocstats.stats_results['classes']['distinct'])
        new_rdfstats.no_of_properties = len(rdfdocstats.stats_results['propertiesall']['distinct'])
        new_rdfstats.no_of_vocabularies = len(rdfdocstats.stats_results['vocabularies'])
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
    else:
        self.triples = None
        new_rdfstats.triples = None
        new_rdfstats.void = None
        new_rdfstats.error = unicode(error)
    new_rdfstats.last_updated = datetime.datetime.now()
    self.rdf_last_updated = new_rdfstats.last_updated

    model.Session.commit()
    
    
def create_error_stats():
    pass    
