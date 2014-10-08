from __future__ import absolute_import
import base64
import inspect
import pickle
import itertools
from pyramid.decorator import reify
from pyramid_admin2 import admin_manager
from cqlengine.models import Model as CQLEngineModel
from cqlengine.exceptions import ValidationError
from cqlengine.query import ModelQuerySet
import cqlengine


def _cqlengine_admin_manager_factory(model):
    if inspect.isclass(model) and issubclass(model, CQLEngineModel):
        return CQLEngineManager(model)
    return None


class CQLEngineBrowseCriteria(admin_manager.BrowseCriteria):


    @staticmethod
    def serialize_pages(pages):
        """ Serialize list of pages
        :param list pages: the list of pages
        :return: serialized string
        :rtype: str

        >>> from datetime import datetime
        >>> pages = [{'part':1234, 'id': datetime(2014, 2, 14)}, {'part': 1234, 'id': datetime(2014, 2, 17)}]
        >>> CQLEngineBrowseCriteria.serialize_pages(pages)
        'gANdcQAofXEBKFgEAAAAcGFydHECTdIEWAIAAABpZHEDY2RhdGV0aW1lCmRhdGV0aW1lCnEEQwoH3gIOAAAAAAAAcQWFcQZScQd1fXEIKGgCTdIEaANoBEMKB94CEQAAAAAAAHEJhXEKUnELdWUu'
        """
        pages = pickle.dumps(pages)
        pages = base64.b64encode(pages)
        return pages.decode('utf-8')

    @staticmethod
    def deserialize_pages(pages):
        """ Deserialize pages into list
        :param string pages: the pages as serialized string
        :return: pages as list
        :rtype: list
        >>> s = 'gANdcQAofXEBKFgEAAAAcGFydHECTdIEWAIAAABpZHEDY2RhdGV0aW1lCmRhdGV0aW1lCnEEQwoH3gIOAAAAAAAAcQWFcQZScQd1fXEIKGgCTdIEaANoBEMKB94CEQAAAAAAAHEJhXEKUnELdWUu'
        >>> CQLEngineBrowseCriteria.deserialize_pages(s)
        [{'part': 1234, 'id': datetime.datetime(2014, 2, 14, 0, 0)}, {'part': 1234, 'id': datetime.datetime(2014, 2, 17, 0, 0)}]
        """
        pages = base64.b64decode(pages)
        pages = pickle.loads(pages)
        return pages

    @reify
    def partition_columns_name(self):
        names = [c.column_name
                 for c in self.model._columns.values() if c.partition_key]
        assert len(names) <= 1, 'Multi partition keys are not tested'
        return names

    @reify
    def primary_key_columns_name(self):
        return [c.column_name
                for c in self.model._columns.values()
                if c.primary_key and not c.partition_key]

    @reify
    def pages(self):
        """
        Get return of checkpoints
        :return:
        :rtype: list
        """
        pages = self.request.GET.get('_pages', None)
        if not pages:
            return []
        return CQLEngineBrowseCriteria.deserialize_pages(pages)

    @property
    def page_status(self):
        return 'Page %d' % (len(self.pages) + 1)

    @reify
    def _previous_page_query(self):
        pages = self.pages.copy()
        """:type : list"""
        if not len(pages):
            return None
        pages.pop()
        pages = CQLEngineBrowseCriteria.serialize_pages(pages)
        return {
            '_pages': pages,
        }

    @reify
    def _next_page_query(self):
        objs = self.objects
        if not len(objs) or len(objs) < self.items_per_page:
            return None
        obj = self.objects[-1]
        pages = self.pages.copy()
        page = {}
        for cname in itertools.chain(self.partition_columns_name,
                                     self.primary_key_columns_name):
            page[cname] = obj.__getattribute__(cname)
        pages.append(page)
        pages = CQLEngineBrowseCriteria.serialize_pages(pages)
        return {
            '_pages': pages,
        }

    @reify
    def objects(self):
        pages = self.pages.copy()
        raw_query = self.model.objects.limit(self.items_per_page)
        if not len(pages):
            return list(raw_query)
        page = pages.pop()
        if len(self.primary_key_columns_name):
            partition_key = self.partition_columns_name[0]
            filters = {
                partition_key: page[partition_key]
            }
            for cname in self.primary_key_columns_name:
                filters['%s__gte' % cname] = page[cname]
            objs = list(raw_query.filter(**filters))
            if len(objs) < self.items_per_page:
                query = raw_query.limit(self.items_per_page - len(objs))
                query = query.filter(pk__token__gt =
                                     cqlengine.Token(page[partition_key]))
                objs = objs + list(query)
        else:
            for cname in self.partition_columns_name:
                # this because there is only <= 1 partition key
                query = raw_query.filter(pk__token__gt =
                                         cqlengine.Token(page[cname]))
            objs = list(query)
        return objs


class CQLEngineManager(admin_manager.AdminManager):

    __default_criteria_cls__ = CQLEngineBrowseCriteria

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
        try:
            return self.model.get(**id_filters)
        except (ValidationError, self.model.DoesNotExist):
            return None

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


def includeme(config):
    admin_manager.register_manager_factory(_cqlengine_admin_manager_factory)