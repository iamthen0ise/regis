# Project Title

Regis is a compact yet powerful Python library designed to manage Singleton Registries with added permission checks.

Aimed at offering a blend of simplicity and robustness, Regis allows seamless registration and deregistration of classes while ensuring thread-safety, making it an ideal choice for applications where concurrent access to resources is prevalent.

[![GitHub license](https://img.shields.io/github/license/iamthen0ise/regis)](https://github.com/iamthen0ise/regis/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/iamthen0ise/regis)](https://github.com/iamthen0ise/regis/issues)

## Table of Contents

- [Project Title](#project-title)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)

## Installation
```sh

pip install regis-py

```


## Usage


```python
from regis import Registry, RegistryMixin

# Define a class that will use the registry
class ExampleClass(RegistryMixin):
    def __init__(self, name):
        self.name = name
        self.register()

# Create an instance of the class
example_instance = ExampleClass('ExampleInstance')

# Set an item in the registry
key = 'example_key'
value = 'example_value'
example_instance.set_item(key, value)

# Retrieve the item from the registry
retrieved_value = example_instance.get_item(key)
print(f'Retrieved value from registry: {retrieved_value}')  # Output: Retrieved value from registry: example_value

# Unregister the class instance from the registry
example_instance.unregister()

# Attempting to retrieve the item again will raise a PermissionError since the class instance is unregistered
try:
    example_instance.get_item(key)
except PermissionError:
    print(f'{example_instance.name} does not have permission to access the registry.')
```
