import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import datetime
import lodstats.stats as stats
import logging
import RDF


log = logging.getLogger(__name__)


class UserController(base.BaseController):
    def recommendation(self, id=None, type_='topic'):
        context = {'model': model,
                   'session': model.Session,
                   'user': base.c.user or base.c.author}
        data_dict = {'id': base.c.user.id,
                     'user_obj': c.userobj}
                     
                     
                     
        import ipdb; ipdb.set_trace()
        c.is_sysadmin = Authorizer().is_sysadmin(c.user)
        try:
            user_dict = logic.get_action('user_show')(context, data_dict)
        except NotFound:
            base.h.redirect_to(controller='user', action='login', id=None)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))
        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = self._format_about(user_dict['about'])
        base.c.type = type_
        return base.render('recommendation.html')
