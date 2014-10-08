__author__ = 'tarzan'

import six
if six.PY2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode
import inspect
import deform
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from ..helpers import cell_datatype
from .. import resources as _rsr, admin_manager
import colander
from pyramid.traversal import lineage


def _none_to_colander_null(data):
    return {k: v if v is not None else colander.null for k, v in data.items()}


def _colander_null_to_none(data):
    return {k: v if v is not colander.null else None for k, v in data.items()}


class InvalidSchemaClassError(RuntimeError):
    def __init__(self, admin_mgr):
        """
        :type admin_mgr: pyramid_admin2.admin_manager.AdminManager
        """
        self.admin_mgr = admin_mgr
        super(InvalidSchemaClassError, self).__init__('%s is not class for %s\'s schema'
                                                      % (self.admin_mgr.schema_cls,
                                                         self.admin_mgr.model))


@view_config(context=InvalidSchemaClassError, renderer='pyramid_admin2:templates/no_schema.mak')
def on_invalid_schema_class(context, request):
    return {
        'error': context,
    }


class ModelView(object):
    def __init__(self, context, request):
        """
        :type context: pyramid_admin2.resources.ModelResource
        :type request: pyramid.request.Request
        """
        self.context = context
        self.request = request

    @property
    def model(self):
        return self.context.model

    @property
    def criteria(self):
        """
        :rtype: pyramid_admin2.admin_manager.BrowseCriteria
        """
        return self.admin_mgr.create_criteria(self.request)

    @property
    def is_current_context_object(self):
        """
        :rtype : bool
        """
        return isinstance(self.context, _rsr.ObjectResource)

    @property
    def admin_mgr(self):
        """
        :rtype : pyramid_admin2.admin_manager.AdminManager
        """
        return admin_manager.get_manager(self.model)

    @property
    def model_schema_cls(self):
        if not inspect.isclass(self.admin_mgr.schema_cls):
            raise InvalidSchemaClassError(self.admin_mgr)
        # assert inspect.isclass(self.backend_mgr.schema_cls), \
        #     '%s.__backend_schema_cls__ (%s) is not a class' % \
        #     (self.model.__name__, self.backend_mgr.schema_cls)
        return self.admin_mgr.schema_cls

    def cell_datatype(self, val):
        return cell_datatype(val)

    @property
    def toolbar_actions(self):
        actions = self.model_actions
        if isinstance(self.context, self.admin_mgr.ObjectResource):
            actions += self.object_actions(self.context.object)
        return actions

    @property
    def model_actions(self):
        actions = []
        for aconf in self.admin_mgr.actions:
            if aconf.is_model_action:
                actions.append({
                    'url': _rsr.model_url(self.request, self.model, aconf.conf['name']),
                    'label': aconf.get_label(None),
                    'icon': aconf.icon,
                })
        return actions

    def object_actions(self, obj):
        actions = []
        for aconf in self.admin_mgr.actions:
            if aconf.is_object_action:
                label = aconf.label
                label = label % {
                    'obj': obj,
                    'mgr': self.admin_mgr,
                }
                actions.append({
                    'url': _rsr.object_url(self.request, obj, aconf.conf['name']),
                    'label': aconf.get_label(obj),
                    'icon': aconf.icon,
                    'onclick': aconf.get_onclick(obj),
                })
        return actions

    @property
    def breadcrumbs(self):
        cxt = self.context
        cxts = list(reversed(list(lineage(cxt))))
        r = self.request
        if not r.view_name:
            if self.is_current_context_object:
                cmd_name = 'detail'
            else:
                cmd_name = 'list'
            # cxts = cxts[:-1]
        else:
            cmd_name = r.view_name

        _label = '@' + cmd_name
        for aconf in self.admin_mgr.actions:
            if cmd_name == aconf.name:
                if self.is_current_context_object:
                    _label = aconf.get_label(cxt.object)
                else:
                    _label = aconf.get_label()
                break

        return [{
            'url': r.resource_url(c),
            'label': u'%s' % c,
        } for c in cxts] + [_label, ]

    def list_page_url(self, page, partial=False):
        params = self.request.GET.copy()
        params["_page"] = page
        if partial:
            params["partial"] = "1"
        qs = urlencode(params, True)
        return "%s?%s" % (self.request.path, qs)

    def action_list(self):
        search_schema_cls = self.admin_mgr.search_schema_cls
        if search_schema_cls is None:
            search_form = None
        else:
            search_schema = search_schema_cls().bind()
            search_form = deform.Form(search_schema,
                method='GET',
                appstruct=self.request.GET.mixed(),
                buttons=(deform.Button(title='Search'), )
            )
        return {
            'view': self,
            'admin_mgr': self.admin_mgr,
            'criteria': self.criteria,
            'search_form': search_form,
        }

    def action_create(self):
        schema = self.model_schema_cls().bind()
        form = deform.Form(schema,
                           buttons=(deform.Button(title='Create'),
                                    deform.Button(title='Cancel', type='reset', name='cancel')))

        if 'submit' in self.request.POST:
            try:
                data = form.validate(self.request.POST.items())
                data = _colander_null_to_none(data)
                obj = self.admin_mgr.create(data)
                self.request.session.flash(u'"%s" was created successful.' % obj, queue='pyramid_admin')
                return HTTPFound(_rsr.object_url(self.request, obj))
            except deform.ValidationFailure as e:
                pass

        return {
            'view': self,
            "form": form,
            'admin_mgr': self.admin_mgr,
        }

    def action_update(self):
        obj = self.context.object
        schema = self.model_schema_cls().bind(obj=obj)
        """:type schema: colander.Schema"""
        appstruct = _none_to_colander_null({k: obj.__getattribute__(k)
                                            for k in self.admin_mgr.column_names})
        form = deform.Form(schema,
                           appstruct=appstruct,
                           buttons=(deform.Button(title='Update'),
                                    deform.Button(title='Cancel', type='reset', name='cancel')))

        if 'submit' in self.request.POST:
            try:
                data = form.validate(self.request.POST.items())
                data = _colander_null_to_none(data)
                obj = self.admin_mgr.update(obj, data)
                self.request.session.flash(u'"%s" was updated successful.' % obj, queue='pyramid_admin')
                return HTTPFound(_rsr.object_url(self.request, obj))
            except deform.ValidationFailure as e:
                pass

        return {
            'view': self,
            'obj': obj,
            "form": form,
            'admin_mgr': self.admin_mgr,
        }

    def action_detail(self):
        return {
            'view': self,
            'obj': self.context.object,
            'admin_mgr': self.admin_mgr,
        }

    def action_delete(self):
        obj = self.context.object
        self.admin_mgr.delete(obj)
        self.request.session.flash(u'%s#%s was history!' % (self.admin_mgr.display_name, obj))
        return HTTPFound(_rsr.model_url(self.request, self.model))
