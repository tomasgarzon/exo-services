import importlib


def load_class(package_name):
    path_bits = package_name.split('.')
    # Cut off the class name at the end.
    class_name = path_bits.pop()
    module_path = '.'.join(path_bits)
    module_itself = importlib.import_module(module_path)

    if not hasattr(module_itself, class_name):
        raise ImportError("The Python module '%s' has no '%s' class." % (module_path, class_name))

    return getattr(module_itself, class_name)


def dump_class(instance):
    return '{}.{}'.format(
        instance.__class__.__module__,
        instance.__class__.__name__,
    )
