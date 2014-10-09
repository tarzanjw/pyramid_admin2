from . import (
    model as model_helper,
    get_manager,
    resources as _rsr
)
import venusian
from .views.model_view import ModelView
from .action_conf import ActionConf


def _register_model_view(config, model, view=None, actions=None):
    """
    Add a view for a model
    :type config: pyramid.config.Configurator
    """
    mgr = get_manager(model)
    """:type : pyramid_admin2.admin_manager.AdminManager"""
    if actions is None:
        actions = mgr.admin_actions
    for action_conf in actions:
        aconf = ActionConf.create_from_config(model, action_conf)
        _register_action(config, view, aconf)


def _register_action(config, view, aconf):
    """ Register an action by its configuration
    :type config: pyramid.config.Configurator
    :param class|func view: the view to support this action
    :param ActionConf aconf: the action configuration
    :return:
    """
    # todo implement here
    if view is None:
        view = ModelView
    mgr = get_manager(aconf.model)
    mgr.actions.append(aconf)
    config.add_view(view, **aconf.view_conf)


def _register_object_action(config, view, name, model, aconf):
    """
    Register an object action for a model
    :type config: pyramid.config.Configurator
    :param class|func view: the view to support this action
    :param string name: name of the action
    :param class model: the model
    :param ActionConf aconf: the action configuration
    :return:
    """
    aconf['context'] = _rsr.ObjectResource
    aconf = ActionConf(name, model, aconf)
    _register_action(config, view, aconf)


class _action_view_config(object):
    _register_action_fn = None

    def __init__(self, model, name=None, **kwargs):
        assert model, "You have to specify model"
        self.model = model
        self.action_name = name
        self.conf = kwargs
        self.conf.setdefault('name', name)

    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            conf = self.conf.copy()
            self.__class__._register_action_fn(scanner.config,
                             ob,
                             self.action_name,
                             self.model,
                             conf)
        info = venusian.attach(wrapped, callback,
                               category='pyramid_admin2')
        """:type : venusian.AttachInfo"""

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if not self.conf.get('attr'):
                self.conf['attr'] = wrapped.__name__
        if self.action_name is None:
            self.action_name = wrapped.__name__
        return wrapped
#
#
# class model_action_config(_action_view_config):
#     _add_action_fn = staticmethod(add_model_action)
#
#
class object_action_config(_action_view_config):
    _register_action_fn = staticmethod(_register_object_action)