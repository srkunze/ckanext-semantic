import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.similarity.methods as similarity_methods
import ckanext.lodstatsext.model.recommendation as r
import datetime
import lodstats.stats as stats
import logging
import RDF


log = logging.getLogger(__name__)


class RecommendationController(base.BaseController):
    def read(self, similarity_method=None):
        context = {'model': model,
                   'session': model.Session,
                   'user': base.c.user or base.c.author}
        data_dict = {'id': base.c.user,
                     'user_obj': base.c.userobj}

        try:
            user_dict = logic.get_action('user_show')(context, data_dict)
        except NotFound:
            base.h.redirect_to(controller='user', action='login', id=None)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))
        base.c.user_dict = user_dict
        base.c.is_myself = user_dict['name'] == base.c.user
        
        if similarity_method == None:
            similarity_methods = ['topic']
#           similarity_methods = ['topic', 'location', 'time']
        else:
            similarity_methods = [similarity_method]
            
        if similarity_method == None:
            base.c.content_heading = 'Datasets that match your interests'
        elif similarity_method == 'topic':
            base.c.content_heading = 'Datasets matching your interests topic-wise'
        elif similarity_method == 'location':
            base.c.content_heading = 'Datasets that are from a location you might be interested in'
        elif similarity_method == 'time':
            base.c.content_heading = 'Datasets that are from a time you could be interested in'
        
        recommended = r.Recommendation(base.c.userobj)
        for method_name in similarity_methods:
            recommended.set_count_limit(5)
            base.c.user_dict['recommended_datasets'] = recommended.datasets(method_name)
            
            base.c.user_dict['recommended_datasets'] = [model_dictize.package_dictize(x, context) for x in base.c.user_dict['recommended_datasets'].keys()]
        
        return base.render('recommendation.html')
