from pyramid.view import view_config
from .. import resources as _rsr, ROOT_ROUTE_NAME, model as model_helper

__author__ = 'tarzan'

@view_config(route_name=ROOT_ROUTE_NAME, context=_rsr.AdminSite,
             renderer='pyramid_admin2:templates/index.mak')
def admin_site_home_view(request):
    """
    :type request: pyramid.request.Request
    """
    models = model_helper.get_registered_models()
    return {
        'models': [dict(
            name=m.__name__,
            url=_rsr.model_url(request, m)
        ) for m in models]
    }