import urllib
import six
import pyramid_admin2 as pa
from . import model as model_helper
from .admin_manager import get_manager

__author__ = 'tarzan'


def model_url(request, model, action=None, query=None):
    """
    Get url for an model with its action
    :type request: pyramid.request.Request
    :type model: object
    :type action: string
    :type query: string or dict
    """
    model = model_helper.get_registered_model(model)
    mgr = get_manager(model)

    url = pa.ADMIN_SITE_PATH + mgr.slug
    if action:
        url += '/' + action
    if query and isinstance(query, dict):
        query = urllib.urlencode(query)
    if query:
        url += '?' + query
    return request.relative_url(url, True)


def object_url(request, obj, action=None, query=None):
    if not obj:
        return ''
    if isinstance(obj, type):
        model = obj
    else:
        model = obj.__class__
    mgr = get_manager(model)
    obj_id = mgr.object_id(obj)
    url = pa.ADMIN_SITE_PATH + mgr.slug + '/' + six.text_type(obj_id)
    if action:
        url += '/' + action
    if query and isinstance(query, dict):
        query = urllib.urlencode(query)
    if query:
        url += '?' + query
    return request.relative_url(url, True)


class ModelResource(object):
    model = None

    def __init__(self, parent, name):
        """
        :type parent: AdminSite
        """
        self.__parent__ = parent
        self.__name__ = name
        self.request = parent.request

    @property
    def admin_mgr(self):
        """
        :rtype : pyramid_admin2.admin_manager.AdminManager
        """
        return get_manager(self.model)

    def __getitem__(self, id_value):
        obj = self.admin_mgr.get_object(id_value)
        if obj:
            return self.admin_mgr.ObjectResource(self, id_value, obj)
        raise KeyError('%s#%s not found' % (self.admin_mgr.display_name, id_value))

    def __resource_url__(self, *args, **kwargs):
        return model_url(self.request, self.model)

    def __unicode__(self):
        return six.text_type(self.model.__name__)

    def __str__(self):
        if six.PY2:
            return self.__unicode__().encode('utf-8')
        else:
            return self.model.__name__


class ObjectResource(object):
    url = '#'

    def __init__(self, parent, name, object):
        """
        :type parent: ModelResource
        """
        self.__parent__ = parent
        self.__name__ = name
        self.model = parent.model
        self.request = parent.request
        self.object = object

    def __resource_url__(self, *args, **kwargs):
        return object_url(self.request, self.object)

    def __unicode__(self):
        return six.text_type('%s').format(self.object)

    def __str__(self):
        return str(self.__unicode__())


_AUTO_CLASSES = {}


def model_resource_class(model):
    global _AUTO_CLASSES
    cls_name = model.__name__ + '_ModelResource'
    try:
        return _AUTO_CLASSES[cls_name]
    except KeyError:
        cls = type(cls_name, (ModelResource,), {
        'model': model,
        })
        _AUTO_CLASSES[cls_name] = cls
        return cls


def object_resource_class(model):
    global _AUTO_CLASSES
    cls_name = model.__name__ + '_ObjectResource'
    try:
        return _AUTO_CLASSES[cls_name]
    except KeyError:
        cls = type(cls_name, (ObjectResource,), {
        'model': model,
        })
        _AUTO_CLASSES[cls_name] = cls
        return cls


class AdminSite(object):
    __acl__ = [
    ]
    model_mappings = {

    }

    __parent__ = None
    __name__ = ''
    # @property
    # def __name__(self):
    #     return pb.ADMIN_SITE_PATH.strip('/')

    def __init__(self, request):
        """
        :type request: pyramid.request.Request
        """
        self.request = request

    def __getitem__(self, item):
        try:
            model = AdminSite.model_mappings[item]
        except KeyError as e:
            for model in model_helper.get_registered_models():
                mgr = get_manager(model)
                if mgr.slug == item:
                    AdminSite.model_mappings[item] = model
                    break
            else:
                raise e
        mgr = get_manager(model)
        return mgr.ModelResource(self, item)

    def __resource_url__(self, *args, **kwargs):
        return self.request.application_url + '/' + pa.ADMIN_SITE_PATH.strip('/') + '/'

    def __unicode__(self):
        return six.text_type('Backend')

    def __str__(self):
        return str(self.__unicode__())
