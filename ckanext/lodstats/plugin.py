import os
from logging import getLogger

from pylons import request
from genshi.input import HTML
from genshi.filters.transform import Transformer

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IConfigurer
from ckan.plugins import IGenshiStreamFilter
from ckan.plugins import IRoutes

log = getLogger(__name__)


class LODstatsPlugin(SingletonPlugin):
    """This plugin demonstrates how a theme packaged as a CKAN
    extension might extend CKAN behaviour.

    In this case, we implement three extension interfaces:

      - ``IConfigurer`` allows us to override configuration normally
        found in the ``ini``-file.  Here we use it to specify the site
        title, and to tell CKAN to look in this package for templates
        and resources that customise the core look and feel.
        
      - ``IRoutes`` allows us to add new URLs, or override existing
        URLs.  In this example we use it to override the default
        ``/register`` behaviour with a custom controller
    """
    implements(IConfigurer, inherit=True)
    #implements(IRoutes, inherit=True)

    def update_config(self, config):
        """This IConfigurer implementation causes CKAN to look in the
        ```public``` and ```templates``` directories present in this
        package for any customisations.

        It also shows how to set the site title here (rather than in
        the main site .ini file), and causes CKAN to use the
        customised package form defined in ``package_form.py`` in this
        directory.
        """
        # set the title
        config['ckan.site_title'] = "Example CKAN theme"
 

    #def before_map(self, map):
        """This IRoutes implementation overrides the standard
        ``/user/register`` behaviour with a custom controller.  You
        might instead use it to provide a completely new page, for
        example.

        Note that we have also provided a custom register form
        template at ``theme/templates/user/register.html``.

        # Hook in our custom user controller at the points of creation
        # and edition.
        map.connect('/user/register',
                    controller='ckanext.example.controller:CustomUserController',
                    action='register')
        map.connect('/user/edit',
                    controller='ckanext.example.controller:CustomUserController',
                    action='edit')
        map.connect('/user/edit/{id:.*}',
                    controller='ckanext.example.controller:CustomUserController',
                    action='edit')

        map.connect('/package/new', controller='package_formalchemy', action='new')
        map.connect('/package/edit/{id}', controller='package_formalchemy', action='edit')
        """
        #return map
