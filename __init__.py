import weakref
from collections.abc import Hashable
from typing import Type, Any, Dict

class SingletonMeta(type):
    """A metaclass for creating Singleton classes."""
    _instances = weakref.WeakKeyDictionary()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Registry(metaclass=SingletonMeta):
    """A Singleton registry class for managing access to specific resources."""

    def __init__(self):
        self._items: Dict[Any, Any] = {}
        self._registered_classes = weakref.WeakSet()

    def register_class(self, caller: Type[Any]):
        """Register a class with permission to access the registry."""
        self._registered_classes.add(caller)

    def unregister_class(self, caller: Type[Any]):
        """Unregister a class to revoke its access to the registry."""
        self._registered_classes.discard(caller)

    def _check_permissions(self, caller: Type[Any]):
        """Check if the calling class has permission to access the registry."""
        if caller not in self._registered_classes:
            raise PermissionError(f"Class {caller} has no permission to access the registry.")

    def set_item(self, caller: Type[Any], key: Any, item: Any):
        """Set an item in the registry with permission checking."""
        if not isinstance(key, Hashable):
            raise TypeError(f"Key must be hashable, but got {type(key).__name__}")
        self._check_permissions(caller)
        self._items[key] = item

    def get_item(self, caller: Type[Any], key: Any) -> Any:
        """Get an item from the registry with permission checking."""
        if not isinstance(key, Hashable):
            raise TypeError(f"Key must be hashable, but got {type(key).__name__}")
        self._check_permissions(caller)
        return self._items[key]

class RegistryMixin:
    """A mixin class for interacting with the registry."""

    def register_registry(self) -> None:
        """Register the current class with the registry."""
        self.registry = Registry()
        self.registry.register_class(self.__class__)

    def unregister_registry(self) -> None:
        """Unregister the current class from the registry."""
        self.registry.unregister_class(self.__class__)

    def set_item(self, key: Any, item: Any) -> None:
        """Set an item in the registry."""
        self.registry.set_item(self.__class__, key, item)

    def get_item(self, key: Any) -> Any:
        """Get an item from the registry."""
        return self.registry.get_item(self.__class__, key)
