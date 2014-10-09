import six
from . import resources as _rsr, ROOT_ROUTE_NAME, admin_manager


__author__ = 'tarzan'


_DEFAULT_ACTION_CONF = {
    'list': {
        'route_name': ROOT_ROUTE_NAME,
        'context': _rsr.ModelResource,
        'name': '',
        'attr': 'action_list',
        'renderer': 'pyramid_admin2:templates/list.mak',
        'permission': 'list',
        '_icon': 'list',
        '_label': six.text_type('{mgr.display_name} list'),
    },
    'create': {
        'route_name': ROOT_ROUTE_NAME,
        'context': _rsr.ModelResource,
        'name': 'create',
        'attr': 'action_create',
        'renderer': 'pyramid_admin2:templates/create.mak',
        'permission': 'create',
        '_icon': 'plus',
        '_label': six.text_type('Create new {mgr.display_name}'),
    },
    'detail': {
        'route_name': ROOT_ROUTE_NAME,
        'context': _rsr.ObjectResource,
        'name': '',
        'attr': 'action_detail',
        'renderer': 'pyramid_admin2:templates/detail.mak',
        'permission': 'detail',
        '_icon': 'eye-open',
        '_label': six.text_type('View {obj} detail'),
    },
    'update': {
        'route_name': ROOT_ROUTE_NAME,
        'context': _rsr.ObjectResource,
        'name': 'update',
        'attr': 'action_update',
        'renderer': 'pyramid_admin2:templates/update.mak',
        'permission': 'update',
        '_icon': 'pencil',
        '_label': six.text_type('Update {obj}'),
    },
    'delete': {
        'route_name': ROOT_ROUTE_NAME,
        'context': _rsr.ObjectResource,
        'name': 'delete',
        'attr': 'action_delete',
        'permission': 'delete',
        '_icon': 'remove',
        '_label': six.text_type('Delete {obj}'),
        '_onclick': six.text_type("return confirm('Do you want to delete {obj}?');"),
    },
}

class ActionConf(object):
    """ this class is used to configure an action for a model or object
    """
    @classmethod
    def create_from_config(cls, model, conf):
        """ Create an action config from quick config
        The quick config can be:
          1. a string: the name of action (with default config is in this module)
          2. a 2 elements tuple/list: with 1st element is action name, 2nd element
             is action config
        :param model:
        :param conf:
        :return:
        """
        assert bool(conf), 'Can not be empty configuration'
        if not isinstance(conf, (list, tuple,)):
            assert conf in _DEFAULT_ACTION_CONF, \
                'Unknown action named "%s"' % conf
            action_name = conf
            conf = _DEFAULT_ACTION_CONF[action_name].copy()
        else:
            action_name, conf = conf
        return ActionConf(action_name, model, conf)

    def __init__(self, name, model, conf):
        """
        :param string name: action's name
        :param class model: the model
        :param dict conf: action's configuration
        :return:
        """
        self.name = name
        self.model = model
        assert 'context' in conf
        if conf['context'] is _rsr.ObjectResource:
            conf['context'] = _rsr.object_resource_class(self.model)
        elif conf['context'] is _rsr.ModelResource:
            conf['context'] = _rsr.model_resource_class(self.model)
        conf.setdefault('name', None)
        self.conf = conf

    @property
    def is_model_action(self):
        return issubclass(self.context, _rsr.ModelResource)

    @property
    def is_object_action(self):
        return issubclass(self.context, _rsr.ObjectResource)

    @property
    def view_conf(self):
        conf = {k: v for k, v in self.conf.items() if not k.startswith('_')}
        conf['route_name'] = ROOT_ROUTE_NAME
        return conf

    @property
    def label(self):
        try:
            return self.conf['_label']
        except KeyError:
            if self.is_model_action:
                return '{mgr.display_name}@' + self.name
            else:
                return '{obj}@' + self.name

    def get_label(self, obj=None):
        return self.label.format(
            mgr=admin_manager.get_manager(self.model),
            obj=obj,
            )

    def get_onclick(self, obj=None):
        onclick = self.conf.get('_onclick', None)
        if onclick:
            onclick = onclick.format(
                mgr=admin_manager.get_manager(self.model),
                obj=obj,
                )
        return onclick

    @property
    def icon(self):
        return self.conf.get('_icon', None)

    def __getitem__(self, item):
        return self.conf[item]

    def __getattr__(self, item):
        try:
            return self.conf[item]
        except KeyError:
            raise AttributeError
