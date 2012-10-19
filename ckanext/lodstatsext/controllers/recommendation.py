import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize
import ckanext.lodstatsext.lib.helpers as h
import ckanext.lodstatsext.model.prefix as prefix
import ckanext.lodstatsext.model.similarity.methods as similarity_methods
import ckanext.lodstatsext.model.recommendation as r
import datetime
import lodstats.stats as stats
import logging
import RDF


log = logging.getLogger(__name__)


class RecommendationController(base.BaseController):
    def read(self, type_=None):
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
        
            
        recommendation = r.Recommendation(base.c.userobj)
        recommendation.set_recommended_entity_class(str(prefix.void.Dataset.uri))
         
        if type_ == None:
           types = ['topic', 'location', 'time']
           recommendation.set_count_limit(3)
        else:
            types = [type_]
            recommendation.set_count_limit(10)

        base.c.recommendation = {}
        for type_ in types:
            recommendation.set_type(type_)
            recommendation.load()
            for dataset, reasons in recommendation.entities.iteritems():
                dataset_dict = model_dictize.package_dictize(dataset, context)
                dataset_dict['reasons'] = reasons
                
                if base.c.recommendation.has_key(type_):
                    base.c.recommendation[type_].append(dataset_dict)
                else:
                    base.c.recommendation[type_] = [dataset_dict]

       
        return base.render('recommendation.html')
