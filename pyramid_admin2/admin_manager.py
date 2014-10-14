import inspect
import itertools
from pyramid.decorator import reify
import six
if six.PY2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode
from . import helpers
from .model import register_model
from .helpers import cell_datatype


__author__ = 'tarzan'

ID_SEPARATOR = ','


class AttrDisplayConf(object):
    """ This class is used to normalize a configuration for attribute display
    """
    def __init__(self, attr_name, *args):
        self.attr_name = attr_name

        def first_instance(types, default):
            for arg in args:
                if isinstance(arg, types):
                    return arg
            return default

        self.label = first_instance(six.string_types, helpers.name_to_words(attr_name))
        self.limit = first_instance(six.integer_types, 5)


class ConfigurablePropertyDescriptor(object):
    """ This class support some properties for AdminManager that can be configured
    from Model class with __admin_ prefix
    """
    def __init__(self, property_name):
        self.name = property_name
        self.cfg_attr_name = '__admin_%s__' % self.name
        self.def_attr_name = '__default_%s__' % self.name
        self.container_attr_name = '__%s__' % self.name

    def _normalize_value(self, val):
        return val

    def __get__(self, obj, type=None):
        """
        :param AdminManager obj: the manager instance
        :param type type: the manager class
        :rtype: mixed
        """
        if obj is None:
            return self
        try:
            return obj.__getattribute__(self.container_attr_name)
        except AttributeError:
            try:
                val = getattr(obj.model, self.cfg_attr_name)
            except AttributeError:
                val = obj.__getattribute__(self.def_attr_name)
            val = self._normalize_value(val)
            obj.__setattr__(self.container_attr_name, val)
            return val

    def __set__(self, instance, value):
        raise NotImplementedError('I do not think that you need this feature')


class ForceToListConfigurablePropertyDescriptor(ConfigurablePropertyDescriptor):
    def _normalize_value(self, val):
        if not isinstance(val, (list, tuple)):
            val = [val, ]
        return val


class DisplayConfPropertyDescriptor(ConfigurablePropertyDescriptor):
    def _normalize_value(self, val):
        value = []
        for conf in val:
            if not isinstance(conf, (list, tuple)):
                conf = [conf, ]
            value.append(AttrDisplayConf(*conf))
        return value


class BrowseCriteria(object):
    search_schema = ConfigurablePropertyDescriptor('search_schema')
    __default_search_schema__ = None

    def __init__(self, manager, request):
        """
        :param AdminManager manager: the manager
        :param pyramid.request.Request request: the request that criteria is applied to
        :return:
        """
        self.manager = manager
        self.request = request
        self.model = manager.model
        self.items_per_page = manager.list__items_per_page

    @property
    def objects_count(self):
        return None

    @property
    def objects(self):
        raise NotImplementedError()

    @property
    def page_status(self):
        return None

    @property
    def previous_page_url(self):
        return self._generate_page_url(self._previous_page_query)

    @property
    def next_page_url(self):
        return self._generate_page_url(self._next_page_query)

    def _generate_page_url(self, extend_query_str):
        if not extend_query_str:
            return None
        queries = self.request.GET.mixed()
        queries.update(extend_query_str)
        queries = urlencode(queries)
        return self.request.relative_url('?' + queries)

    @property
    def _previous_page_query(self):
        return None

    @property
    def _next_page_query(self):
        return None


class AdminManager(object):
    """ This class is used to manage all admin operations for a model
    """
    admin_actions = ConfigurablePropertyDescriptor('admin_actions')
    slug = \
        ConfigurablePropertyDescriptor('slug')
    __acl__ = \
        ConfigurablePropertyDescriptor('__acl__')
    display_name = \
        ConfigurablePropertyDescriptor('display_name')
    schema_cls = \
        ConfigurablePropertyDescriptor('schema_cls')
    search_schema_cls = \
        ConfigurablePropertyDescriptor('search_schema_cls')
    id_attr = \
        ForceToListConfigurablePropertyDescriptor('id_attr')
    column_names = \
        ForceToListConfigurablePropertyDescriptor('column_names')
    list__items_per_page = \
        ConfigurablePropertyDescriptor('list__items_per_page')
    list__columns_to_display = \
        DisplayConfPropertyDescriptor('list__columns_to_display')
    detail__columns_to_display = \
        DisplayConfPropertyDescriptor('detail__columns_to_display')
    detail__relations_to_display = \
        DisplayConfPropertyDescriptor('detail__relations_to_display')
    criteria_cls = ConfigurablePropertyDescriptor('criteria_cls')

    __default_criteria_cls__ = BrowseCriteria
    __default_admin_actions__ = ['list', 'create', 'update', 'detail', 'delete']
    __default_schema_cls__ = None
    __default_search_schema_cls__ = None
    __default_id_attr__ = 'id'
    __default_list__items_per_page__ = 20

    @property
    def __default_slug__(self):
        return helpers.name_to_underscore(self.model.__name__)

    @property
    def __default_column_names__(self):
        return dir(self.model)

    @property
    def __default_display_name__(self):
        return helpers.name_to_words(self.model.__name__)

    @property
    def __default_list__columns_to_display__(self):
        return  self.column_names

    @property
    def __default_detail__columns_to_display__(self):
        return  self.column_names

    @property
    def __default_detail__relations_to_display__(self):
        return []

    def __init__(self, model):
        """
        :type model: class
        """
        assert inspect.isclass(model)
        self.model = model
        self.actions = []

    @reify
    def ModelResource(self):
        from . import resources as _rsr
        return _rsr.model_resource_class(self.model)

    @reify
    def ObjectResource(self):
        from . import resources as _rsr
        return _rsr.object_resource_class(self.model)

    def create_criteria(self, request):
        """
        :rtype: BrowseCriteria
        """
        return self.criteria_cls(self, request)

    def get_value_type(self, val):
        """ Get type of a value to display
        :param mixed val: the value
        :return: value's type as string
        :rtype: string
        """
        return cell_datatype(val)

    def get_column_type(self, col_name):
        """ Get type of a column
        :param string col_name: column name
        :return: column's type
        :rtype: str|None
        """
        try:
            return getattr(self.model, '__admin_col_type_%s__' % col_name)
        except AttributeError:
            return None

    def get_display_value(self, val, adc):
        """ Get value of object field to display
        :param AttrDisplayConf adc: the config to display
        """
        val_type = self.get_column_type(adc.attr_name) \
                   or self.get_value_type(val)
        if val_type == 'list':
            return list(itertools.islice(val, adc.limit))
        return val

    def get_info_to_display(self, obj, adc):
        """ Get information to display an attribute of an object
        :param obj: the object
        :param AttrDisplayConf adc: the config to display
        :return: a tuple of type and value
        :rtype: (string, mixed)
        """
        val = obj.__getattribute__(adc.attr_name)
        val_type = self.get_column_type(adc.attr_name) \
                   or self.get_value_type(val)
        return val_type, self.get_display_value(val, adc)

    def get_id_filters(self, id_value):
        id_part_count = len(self.id_attr)
        vals = str(id_value).split(ID_SEPARATOR, id_part_count)
        return dict(zip(self.id_attr, vals))

    def get_object(self, key):
        raise NotImplementedError()

    def object_id(self, obj):
        return six.text_type(ID_SEPARATOR).join([six.text_type(getattr(obj, attr_name))
                                        for attr_name in self.id_attr])


_managers_factory = []


def create_manager(model):
    """
    create backend manager for a model
    :rtype: Manager
    """
    for mf in _managers_factory:
        mgr = mf(model)
        if mgr:
            register_model(model)
            return mgr
    raise NotImplementedError('Can not find backend manager for model "%s"'
                              % model.__name__)


def register_manager_factory(factory):
    global _managers_factory
    _managers_factory.append(factory)


_manager_store = {}


def get_manager(model):
    """
    get backend manager for a model
    :rtype: AdminManager
    """
    global _manager_store
    try:
        return _manager_store[model]
    except KeyError:
        manager = create_manager(model)
        _manager_store[model] = manager
        model.__admin_manager__ = manager
        return manager
