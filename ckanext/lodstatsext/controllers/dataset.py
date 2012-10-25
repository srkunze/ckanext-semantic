import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import datetime
import lodstats.stats as stats
import logging
import RDF


log = logging.getLogger(__name__)



class DatasetController(base.BaseController):
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
        #TODO: retrieve RDF from Virtuoso

        return 0
        
