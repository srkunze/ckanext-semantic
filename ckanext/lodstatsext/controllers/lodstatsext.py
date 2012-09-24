import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckanext.lodstatsext.lib.lodstatsextlib as lodstatsextlib
import datetime
import logging
import RDF

log = logging.getLogger(__name__)


class PackageController(base.BaseController):
    def read_n3(self, id):
        base.response.headers['Content-Type'] = "text/n3; charset=utf-8"

        context = {'model': model, 'session': model.Session,
                   'user': base.c.user or base.c.author, 'extras_as_string': True,
                   'for_view': True}
        data_dict = {'id': id}
        
        split = id.split('@')
        if len(split) == 2:
            data_dict['id'], revision_ref = split
            if model.is_id(revision_ref):
                context['revision_id'] = revision_ref
            else:
                try:
                    date = date_str_to_datetime(revision_ref)
                    context['revision_date'] = date
                except TypeError, e:
                    abort(400, _('Invalid revision format: %r') % e.args)
                except ValueError, e:
                    abort(400, _('Invalid revision format: %r') % e.args)
        elif len(split) > 2:
            abort(400, _('Invalid revision format: %r') %
                  'Too many "@" symbols')

        #check if package exists
        try:
            base.c.pkg_dict = logic.get_action('package_show')(context, data_dict)
        except logic.NotFound:
            abort(404, _('Dataset not found'))
        except logic.NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % id)
            
        dataset = context['package']
        dataset_lodstats, dataset_lodstats_partitions = lodstatsextlib.get_dataset_lodstats(dataset)

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
        ns_urn_uuid = RDF.NS("")

        #import ipdb; ipdb.set_trace()
        url = base.h.url_for(controller='package', action='read', id=dataset.name, qualified=True)
        dataset.uri = RDF.Uri(url)
        
        rdf_model.append(RDF.Statement(dataset.uri, ns_owl.sameAs, RDF.Uri("urn:uuid:" + dataset.id)))
        rdf_model.append(RDF.Statement(dataset.uri, ns_rdf.type, ns_dcat.Dataset))
        rdf_model.append(RDF.Statement(dataset.uri, ns_rdfs.label, dataset.name))
        rdf_model.append(RDF.Statement(dataset.uri, ns_dct.identifier, dataset.name))
        rdf_model.append(RDF.Statement(dataset.uri, ns_dct.title, dataset.title))
        rdf_model.append(RDF.Statement(dataset.uri, ns_dct.description, dataset.notes))
        # + license, author, maintainer

        rdf_model.append(RDF.Statement(dataset.uri, ns_rdf.type, ns_void.Dataset))
        rdf_model.append(RDF.Statement(
            dataset.uri,
            ns_void.triples,
            RDF.Node(literal=str(dataset_lodstats.triple_count), datatype=ns_xs.integer.uri)))
        
        # void:observation extension stuff
        rdf_model.append(RDF.Statement(ns_stats.value, ns_rdf.type, ns_qb.MeasureProperty))
        rdf_model.append(RDF.Statement(ns_stats.subjectsOfType, ns_rdf.type, ns_qb.DimensonProperty))
        rdf_model.append(RDF.Statement(ns_stats.schema, ns_rdf.type, ns_qb.AttributeProperty))
        
        # voidify results from custom stats
        #for stat in custom_stats.stats_to_do:
        #    stat.voidify(void_model, dataset)

        # serialize to string and return
        serializer = RDF.Serializer(name="turtle")
        serializer.set_namespace("xs", "http://www.w3.org/2001/XMLSchema#")
        serializer.set_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        serializer.set_namespace("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        serializer.set_namespace("owl", "http://www.w3.org/2002/07/owl#")
        serializer.set_namespace("void", "http://rdfs.org/ns/void#")
        serializer.set_namespace("dcat", "http://www.w3.org/ns/dcat#")
        serializer.set_namespace("dct", "http://purl.org/dc/terms/")
        serializer.set_namespace("foaf", "http://xmlns.com/foaf/0.1/")
        serializer.set_namespace("qb", "http://purl.org/linked-data/cube#")
        serializer.set_namespace("xstats", "http://example.org/XStats#")
        #dataset = dataset_uri
        #dataset_ns = RDF.NS("%s#" % dataset.__unicode__())
        #serializer.set_namespace("thisdataset", dataset_ns._prefix)
        return serializer.serialize_model_to_string(rdf_model)
        
