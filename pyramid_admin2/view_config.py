from . import model as model_helper, get_manager
from .views.model_view import ModelView
from .action_conf import ActionConf


def register_model_view(config, model, view=None, actions=None):
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
        register_action(config, view, aconf)


def register_action(config, view, aconf):
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

#
# def _add_action_view(config, model, action_name, default_context=None, **kwargs):
#     model_helper.register_model(model)
#     mgr = model.__backend_manager__
#     """:type : pyramid_backend.backend_manager.Manager"""
#     if 'context' not in kwargs:
#         kwargs['context'] = default_context
#     if 'route_name' not in kwargs:
#         kwargs['route_name'] = 'admin_site'
#     if 'name' not in kwargs:
#         kwargs['name'] = action_name
#     action_name, action_conf = mgr.add_action((action_name, kwargs))
#     view_conf = {k: v for k, v in action_conf.items() if not k.startswith('_')}
#     config.add_view(**view_conf)
#
#
# def add_model_action(config, model, action_name, **kwargs):
#     model_helper.register_model(model)
#     mgr = model.__backend_manager__
#     _add_action_view(config, model, action_name, mgr.model_resource, **kwargs)
#
#
# def add_object_action(config, model, action_name, **kwargs):
#     model_helper.register_model(model)
#     mgr = model.__backend_manager__
#     _add_action_view(config, model, action_name, mgr.ObjectResource, **kwargs)
#
#
# class model_view_config(object):
#     def __init__(self, model, actions=None):
#         assert model, "You have to specify model"
#         self.model = model
#         self.actions = actions
#
#     def view_config(self, scanner, name, ob):
#         add_model_view(scanner.config,
#                        self.model,
#                        ob,
#                        actions=self.actions)
#
#     def __call__(self, wrapped):
#         assert inspect.isclass(wrapped), \
#             '@model_view_config can decorate to class only (decorated to %s)' % type(wrapped)
#         info = venusian.attach(wrapped, self.view_config,
#                                category='pyramid_backend')
#         return wrapped
#
#
# class _action_view_config(object):
#     _add_action_fn = None
#
#     def __init__(self, model, name=None, **kwargs):
#         assert model, "You have to specify model"
#         self.model = model
#         self.action_name = name
#         self.conf = kwargs
#
#     def __call__(self, wrapped):
#         def callback(scanner, name, ob):
#             conf = self.conf.copy()
#             conf['view'] = ob
#             self.__class__._add_action_fn(scanner.config,
#                              self.model,
#                              self.action_name,
#                              **conf)
#         info = venusian.attach(wrapped, callback,
#                                category='pyramid_backend')
#         """:type : venusian.AttachInfo"""
#
#         if info.scope == 'class':
#             # if the decorator was attached to a method in a class, or
#             # otherwise executed at class scope, we need to set an
#             # 'attr' into the settings if one isn't already in there
#             if not self.conf.get('attr'):
#                 self.conf['attr'] = wrapped.__name__
#         if self.action_name is None:
#             self.action_name = wrapped.__name__
#         return wrapped
#
#
# class model_action_config(_action_view_config):
#     _add_action_fn = staticmethod(add_model_action)
#
#
# class object_action_config(_action_view_config):
#     _add_action_fn = staticmethod(add_object_action)