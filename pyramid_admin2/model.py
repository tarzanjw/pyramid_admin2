__author__ = 'tarzan'

import inspect

_registered_models = [

]


def get_registered_models():
    return _registered_models

def get_registered_model(model):
    for m in _registered_models:
        if m is model:
            return m
    raise NotImplementedError('%s model has not been implemented' % model.__name__)

def is_registered_model(obj):
    if not inspect.isclass(obj):
        obj = type(obj)
        if not inspect.isclass(obj):
            return False
    return obj in _registered_models

def register_model(model):
    global _registered_models
    if model in _registered_models:
        return
    # model.__backend_manager__ = create_manager(model)
    _registered_models.append(model)