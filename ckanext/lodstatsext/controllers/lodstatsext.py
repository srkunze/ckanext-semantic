import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckanext.lodstatsext.lib.lodstatsext as libext
import datetime
import lodstats.stats as stats
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
            
        rdf_model = libext.create_rdf_model(context['package'])

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

        return serializer.serialize_model_to_string(rdf_model)
        
