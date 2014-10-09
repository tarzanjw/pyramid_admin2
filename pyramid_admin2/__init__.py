__author__ = 'tarzan'

import re

ADMIN_SITE_PATH = None
ROOT_ROUTE_NAME = 'pyramid_admin'

from . import admin_manager
from .admin_manager import get_manager
from . import view_config


def _lookup_object(spec):
    """
    Looks up a module or object from a some.module:func_name specification.
    For backward compatibility, if the spec does not contain ':' character, the
    last '.' will be replaced as ':'
    :param string spec: the specification to be looked up
    """
    if ':' not in spec:
        parts, target = spec.rsplit('.', 1)
    else:
        parts, target = spec.split(':')
    module = __import__(parts)
    for part in parts.split('.')[1:] + ([target] if target else []):
        module = getattr(module, part)
    return module


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    global ADMIN_SITE_PATH
    settings = config.get_settings()

    # get admin site path
    ADMIN_SITE_PATH = settings['pyramid_admin.admin_site']
    ADMIN_SITE_PATH = ADMIN_SITE_PATH.strip('/') + '/'

    from . import resources as _rsr
    from . import model as model_helper
    from . import views

    # configure views and config directives
    _rsr.AdminSite.__name__ = ADMIN_SITE_PATH
    route_pattern = ADMIN_SITE_PATH + '*traverse'
    config.add_route(ROOT_ROUTE_NAME, route_pattern, factory=_rsr.AdminSite)
    config.add_directive('pa_register_model_view', view_config._register_model_view)
    config.add_directive('pa_register_object_action', view_config._register_object_action)

    admin_manager.ID_SEPARATOR = settings.get('pyramid_admin.id_seprator',
                                              admin_manager.ID_SEPARATOR)

    # register models
    model_paths = settings.get('pyramid_admin.models', '')
    model_paths = filter(bool, re.split('\s+', model_paths))
    for path in model_paths:
        if '#' in path:
            path, actions = path.split('#', 1)
            actions = re.split(r'[\s,]+', actions.strip())
        else:
            actions = None
        model = _lookup_object(path)
        config.pa_register_model_view(model, actions=actions)

    config.scan(__name__)