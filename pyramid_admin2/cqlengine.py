import inspect
from pyramid.decorator import reify

__author__ = 'tarzan'

from pyramid_admin2 import admin_manager
from cqlengine.models import Model as CQLEngineModel
from cqlengine.exceptions import ValidationError
from cqlengine.query import ModelQuerySet


def _cqlengine_admin_manager_factory(model):
    if inspect.isclass(model) and issubclass(model, CQLEngineModel):
        return CQLEngineManager(model)
    return None

class CQLEngineManager(admin_manager.AdminManager):

    @reify
    def queryset(self):
        """
        Get query set for current model
        :rtype cqlengine.query.ModelQuerySet
        """
        return self.model.objects

    @property
    def __default_column_names__(self):
        return [c_name for c_name in self.model._columns]

    def column(self, col_name):
        return getattr(self.model, col_name)

    def get_value_type(self, val, adc=None):
        if isinstance(val, ModelQuerySet):
            return 'list'
        return super().get_value_type(val)


    def get_object(self, key):
        id_filters = self.get_id_filters(key)
        return self.model.get(**id_filters)

    def create(self, data):
        obj = self.model.create(**data)
        return obj

    def update(self, obj, data):
        for attr_name in self.id_attr:
            data.pop(attr_name, None)
        obj.update(**data)
        return obj

    def delete(self, obj):
        obj.delete()

    def fetch_objects(self, filters, fulltext=True, page=1):
        criteria = []
        try:
            for name, value in filters.items():
                if name in self.column_names:
                    criteria.append(self.column(name) == value)
        except ValidationError:
            return []
        limit = self.list__items_per_page
        offset = (page-1)*limit
        objs = self.queryset.filter(*criteria).limit(offset + limit)
        return list(objs)[-limit:]

    def count_objects(self, filters):
        return 10000
        criteria = []
        for name, value in filters.items():
            if name in self.column_names:
                criteria.append(self.column(name) == value)
        return self.queryset.filter(*criteria).count()


def includeme(config):
    admin_manager.register_manager_factory(_cqlengine_admin_manager_factory)