# Sourcegraph Python Library

This Python library provides an interface to analyze and visualize code dependencies in GitHub repositories.

> **⚠️ Warning: Currently only supports Python repositories**
> 
> Please note that this library is currently designed to work only with Python repositories. Analysis of repositories in other programming languages is not supported at this time.

## Installation

You can install the Sourcegraph Python library using pip:

```
pip install sourcegraph
```

## Usage

Here's how you can use the Sourcegraph library to analyze a GitHub repository:

```python
from sourcegraph import Sourcegraph

# Initialize the Sourcegraph object with a repository URL
repo = Sourcegraph(repository_url='https://github.com/Ransaka/sinlib.git')

# Generate a dependency graph
repo.run()

# Plot the dependency graph
repo.plot()  # Supports different networkx compatible layouts when plotting

# Get properties of a specific node (function or class)
node_properties = repo.get_node_property('process_text')
print(node_properties)

# Get the total number of nodes in the repository
print(repo.n_nodes)

# Get all functions and classes in the repository
functions_and_classes = repo.get_functions_and_classes
print(functions_and_classes)

# Get dependencies of a specific class or function
tokenizer_dependencies = repo.get_dependencies("Tokenizer")
print(tokenizer_dependencies)
```

## Features

- **Dependency Analysis**: Analyze and visualize the dependencies between functions and classes in a GitHub repository.
- **Code Inspection**: Retrieve detailed information about specific functions or classes, including their definitions and docstrings.
- **Visualization**: Plot dependency graphs using networkx-compatible layouts.

## Main Methods

- `run()`: Generates the dependency graph for the specified repository.
- `plot()`: Visualizes the dependency graph.
- `get_node_property(node_name)`: Retrieves properties of a specific node (function or class).
- `get_functions_and_classes`: Returns a list of all functions and classes in the repository.
- `get_dependencies(node_name)`: Returns the dependencies of a specific function or class.

## Example Output

Getting node properties:
```python
repo.get_node_property('process_text')
# Output:
# {'type': 'function',
#  'name': 'process_text',
#  'definition': "def process_text(t):\n    ...",
#  'file_name': 'preprocessing.py',
#  'docstring': ''}
```

Getting all functions and classes:
```python
repo.get_functions_and_classes
# Output:
# ['Romanizer', 'Tokenizer', 'Transliterator', 'load_tokenizer', ...]
```

Getting dependencies:
```python
repo.get_dependencies("Tokenizer")
# Output:
# {'load_default_vocab_map', 'process_text'}
```

## Limitations

- Currently, this library only supports analysis of Python repositories. Repositories in other programming languages cannot be processed at this time.
- The library assumes that the repository structure follows common Python project conventions.

## Contributing

Contributions to improve the Sourcegraph Python library are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Ransaka/sourcegraph/blob/main/LICENSE) file for details.

## Contact

For any queries or suggestions, please open an issue on the GitHub repository.
