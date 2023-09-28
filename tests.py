import unittest

from regis import PermissionError, Registry, RegistryMixin


class TestRegistry(unittest.TestCase):

    def test_register_class(self):
        registry = Registry()

        class ExampleClass(RegistryMixin):
            pass
        example_instance = ExampleClass()
        example_instance.register()
        self.assertIn(ExampleClass, registry._registered_classes)

    def test_unregister_class(self):
        registry = Registry()

        class ExampleClass(RegistryMixin):
            pass
        example_instance = ExampleClass()
        example_instance.register()
        example_instance.unregister()
        self.assertNotIn(ExampleClass, registry._registered_classes)

    def test_set_item(self):
        registry = Registry()

        class ExampleClass(RegistryMixin):
            pass
        example_instance = ExampleClass()
        example_instance.register()
        example_instance.set_item('key', 'value')
        self.assertEqual(registry._items['key'], 'value')

    def test_get_item(self):

        class ExampleClass(RegistryMixin):
            pass
        example_instance = ExampleClass()
        example_instance.register()
        example_instance.set_item('key', 'value')
        self.assertEqual(example_instance.get_item('key'), 'value')

    def test_permission_error(self):

        class ExampleClass(RegistryMixin):
            pass
        example_instance = ExampleClass()
        with self.assertRaises(PermissionError):
            example_instance.set_item('key', 'value')


if __name__ == '__main__':
    unittest.main()
