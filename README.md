# Overview

The **keyword argument checker** is a Pylint plugin designed to help enforce best practices when using function calls in Python code. The plugin checks whether keyword arguments are used in function calls when necessary.

The plugin focuses on:

- **Detecting missing keyword arguments**: It raises alerts when a function call contains positional arguments but no keyword arguments, which could lead to confusion or unintended behavior, especially in functions with many parameters.
- **Skipping built-in functions and excluded modules**: The plugin avoids unnecessary checks for built-in methods (like `append` or `split`) and excluded modules that are known to be outside the scope of the desired checks.
- **Providing helpful messages**: If a function call is found to violate best practices (e.g., using positional arguments without keyword arguments), the plugin will flag it with a custom error code (`E9001`) and notify the developer to correct it.

# Requirements for Development

Before running the application, ensure you have the following prerequisites installed:

- **Python 3.x** (Python 3.8.20 is preferred)

To install Poetry, use the following command:

```bash
pip install poetry
```

### Installation

1. Navigate to the `./pylint-plugins` directory:

   ```bash
   cd ./pylint-plugins
   ```

2. Set up the virtual environment and install dependencies using Poetry:

   ```bash
   poetry shell
   poetry install
   ```

### Run Application

To run the application, execute:

```bash
pylint --load-plugins=keyword_arg_checker <PATH_OF_FILE>
```

- **Note**: Ensure that the plugin folder is added to `PYTHONPATH`:

   ```bash
   export PYTHONPATH=<PATH>/pylint_plugins/keyword_arg_checker:$PYTHONPATH
   ```

# Poetry Commands You Might Need

- Set up the virtual environment inside the project directory:

   ```bash
   poetry config virtualenvs.in-project true
   ```

- To check the virtual environment configuration:

   ```bash
   poetry config virtualenvs.in-project
   ```

- Install Poetry plugin for shell integration:

   ```bash
   poetry self add poetry-plugin-shell
   ```

