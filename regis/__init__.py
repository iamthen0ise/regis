"""
A module for managing a Singleton Registry with permission checking.
Provides thread-safety and allows registration and deregistration
of classes for access to the registry.
"""

import logging
import threading
import weakref
from collections.abc import Hashable
from functools import wraps
from typing import Callable, Type, Union

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

ValueType = Union[Type, Callable, object]


class RegistryError(Exception):
    """Base class for exceptions in this library."""


class RegistrationError(RegistryError):
    """Raised when registration of a class fails."""


class PermissionError(RegistryError):
    """Raised when a class does not have permission to access the registry."""


def _threaded_safe(method):
    """
    A decorator to make methods thread-safe.

    :param method: The method to be decorated.
    :type method: Callable
    :return: Wrapped method.
    :rtype: Callable
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


def _check_permissions(method):
    """
    A decorator for checking if the calling class has permission
    to access the registry.

    :param method: The method to be decorated.
    :type method: Callable
    :return: Wrapped method.
    :rtype: Callable
    """
    @wraps(method)
    def wrapper(self, caller, *args, **kwargs):
        if caller not in self._registered_classes:
            raise PermissionError(
                f"Class {caller} has no permission to access the registry.",
            )
        return method(self, caller, *args, **kwargs)
    return wrapper


class SingletonMeta(type):
    """
    A metaclass for creating Singleton classes.

    Usage:

    >>> class MyClass(metaclass=SingletonMeta):
    ...     pass
    >>> a = MyClass()
    >>> b = MyClass()
    >>> a is b
    True
    """
    _instances = weakref.WeakKeyDictionary()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Registry(metaclass=SingletonMeta):
    """
    A thread-safe Singleton registry class for managing access
    to specific resources with permission checking.

    >>> registry = Registry()
    >>> class ExampleClass:
    ...     pass
    >>> registry.register_class(ExampleClass)
    >>> registry.unregister_class(ExampleClass)
    """

    def __init__(self):
        self._items = {}
        self._registered_classes = weakref.WeakSet()
        self._lock = threading.Lock()

    @_threaded_safe
    def register_class(self, caller: Type):
        """
        Register a class with permission to access the registry.

        :param caller: The class to be registered.
        :type caller: Type[Any]

        >>> registry = Registry()
        >>> class ExampleClass:
        ...     pass
        >>> registry.register_class(ExampleClass)
        """
        try:
            self._registered_classes.add(caller)
        except Exception as e:
            error_msg = f"Failed to register the class due to error: {e}"
            logger.exception(e)
            raise RegistrationError(error_msg)

    @_threaded_safe
    def unregister_class(self, caller: Type):
        """
        Unregister a class, revoking its permission to access the registry.

        :param caller: The class to be unregistered.
        :type caller: Type[Any]

        >>> registry = Registry()
        >>> class ExampleClass:
        ...     pass
        >>> registry.register_class(ExampleClass)
        >>> registry.unregister_class(ExampleClass)
        """
        try:
            self._registered_classes.discard(caller)
        except Exception as e:
            logger.exception(e)
            error_msg = f"Failed to unregister the class due to error:{e}"
            raise RegistrationError(error_msg)

    @_threaded_safe
    @_check_permissions
    def set_item(self, caller: Type, key: Hashable, item: ValueType):
        """
        Set an item in the registry with a given key.

        :param caller: The calling class.
            It should have permission to access the registry.
        :type caller: Type
        :param key: The key used to store the item in the registry.
        :type key: Hashable
        :param item: The item to be stored in the registry.
        :type item: Any

        >>> registry = Registry()
        >>> class ExampleClass:
        ...     pass
        >>> registry.register_class(ExampleClass)
        >>> registry.set_item(ExampleClass, 'test_key', 'test_item')
        >>> registry.get_item(ExampleClass, 'test_key')
        'test_item'
        """
        if not isinstance(key, Hashable):
            raise TypeError(
                f"Key must be hashable, but got {type(key).__name__}",
            )
        self._items[key] = item

    @_threaded_safe
    @_check_permissions
    def get_item(self, caller: Type, key: Hashable) -> ValueType:
        """
        Retrieve an item from the registry using a given key.

        :param caller: The calling class.
            It should have permission to access the registry.
        :type caller: Type[Any]
        :param key: The key used to retrieve the item from the registry.
        :type key: Hashable
        :return: The item retrieved from the registry.
        :rtype: Any

        >>> registry = Registry()
        >>> class ExampleClass:
        ...     pass
        >>> registry.register_class(ExampleClass)
        >>> registry.set_item(ExampleClass, 'test_key', 'test_item')
        >>> registry.get_item(ExampleClass, 'test_key')
        'test_item'
        """
        if not isinstance(key, Hashable):
            raise TypeError(
                f"Key must be hashable, but got {type(key).__name__}",
            )
        return self._items[key]


class RegistryMixin:
    """
    A mixin class for interacting with the registry.

    >>> class ExampleClass(RegistryMixin):
    ...     pass
    >>> example_instance = ExampleClass()
    >>> example_instance.register()
    >>> example_instance.set_item('key', 'value')
    >>> example_instance.get_item('key')
    'value'
    """

    def register(self):
        """
        Register the class instance with the registry for access.

        >>> class ExampleClass(RegistryMixin):
        ...     pass
        >>> example_instance = ExampleClass()
        >>> example_instance.register()
        """
        self.registry = Registry()
        self.registry.register_class(self.__class__)

    def set_item(self, key, item):
        """
        Set an item in the registry with a given key.

        :param key: The key used to store the item in the registry.
        :type key: Hashable
        :param item: The item to be stored in the registry.
        :type item: Any

        >>> class ExampleClass(RegistryMixin):
        ...     pass
        >>> example_instance = ExampleClass()
        >>> example_instance.register()
        >>> example_instance.set_item('test_key', 'test_item')
        >>> example_instance.get_item('test_key')
        'test_item'
        """
        if not hasattr(self, 'registry'):
            raise PermissionError(
                "Instance is not registered with the registry.",
            )
        self.registry.set_item(self.__class__, key, item)

    def get_item(self, key):
        """
        Retrieve an item from the registry using a given key.

        :param key: The key used to retrieve the item from the registry.
        :type key: Hashable
        :return: The item retrieved from the registry.
        :rtype: Any

        >>> class ExampleClass(RegistryMixin):
        ...     pass
        >>> example_instance = ExampleClass()
        >>> example_instance.register()
        >>> example_instance.set_item('test_key', 'test_item')
        >>> example_instance.get_item('test_key')
        'test_item'
        """
        if not hasattr(self, 'registry'):
            raise PermissionError(
                "Instance is not registered with the registry.",
            )
        return self.registry.get_item(self.__class__, key)

    def unregister(self):
        """
        Unregister the class instance from the registry, revoking its access.

        >>> class ExampleClass(RegistryMixin):
        ...     pass
        >>> example_instance = ExampleClass()
        >>> example_instance.register()
        >>> example_instance.unregister()
        """
        self.registry.unregister_class(self.__class__)

    def __del__(self):
        """
        Unregister the class instance from the registry upon deletion,
        if it is registered.

        Method reserved for GC. For manual deletion please call `.unregister`.
        Note: Relying on `__del__` for cleanup is not guaranteed to be called
        in every Python implementation and, therefore,
        using `.unregister` is recommended.
        >>> registry = Registry()
        >>> class ExampleClass(RegistryMixin):
        ...     pass
        >>> example_instance = ExampleClass()
        >>> example_instance.register()
        >>> del example_instance  # This should unregister the instance
        """
        if hasattr(self, 'registry') and (
            self.__class__ in self.registry._registered_classes
        ):
            self.unregister()
