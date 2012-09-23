import logging
from urllib import urlencode
import datetime

from pylons import config
from pylons.i18n import _
from genshi.template import MarkupTemplate
from genshi.template.text import NewTextTemplate

from ckan.logic import get_action, check_access
from ckan.lib.helpers import date_str_to_datetime
from ckan.lib.base import (request,
                           render,
                           BaseController,
                           model,
                           abort, h, g, c)
from ckan.lib.base import response, redirect, gettext
import ckan.lib.maintain as maintain
from ckan.lib.package_saver import PackageSaver, ValidationException
from ckan.lib.navl.dictization_functions import DataError, unflatten, validate
from ckan.lib.helpers import json
from ckan.logic import NotFound, NotAuthorized, ValidationError
from ckan.logic import (tuplize_dict,
                        clean_dict,
                        parse_params,
                        flatten_to_string_key)
from ckan.lib.i18n import get_lang
import ckan.forms
import ckan.authz
import ckan.rating
import ckan.misc
import ckan.lib.accept as accept
from home import CACHE_PARAMETERS

from ckan.lib.plugins import lookup_package_plugin

log = logging.getLogger(__name__)





class PackageController(BaseController):
    def read(self, id, format='html'):
        print "Hello"
        if not format == 'html':
            ctype, extension, loader = \
                self._content_type_from_extension(format)
            if not ctype:
                # An unknown format, we'll carry on in case it is a
                # revision specifier and re-constitute the original id
                id = "%s.%s" % (id, format)
                ctype, format, loader = "text/html; charset=utf-8", "html", \
                    MarkupTemplate
        else:
            ctype, format, loader = self._content_type_from_accept()

        response.headers['Content-Type'] = ctype

        package_type = self._get_package_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'extras_as_string': True,
                   'for_view': True}
        data_dict = {'id': id}

        # interpret @<revision_id> or @<date> suffix
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
            c.pkg_dict = get_action('package_show')(context, data_dict)
            c.pkg = context['package']
            c.resources_json = json.dumps(c.pkg_dict.get('resources', []))
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % id)

        # used by disqus plugin
        c.current_package_id = c.pkg.id
        c.related_count = c.pkg.related_count

        # Add the package's activity stream (already rendered to HTML) to the
        # template context for the package/read.html template to retrieve
        # later.
        c.package_activity_stream = \
            get_action('package_activity_list_html')(
                context, {'id': c.current_package_id})

        PackageSaver().render_package(c.pkg_dict, context)

        template = self._read_template(package_type)
        template = template[:template.index('.') + 1] + format

        return render(template, loader_class=loader)
