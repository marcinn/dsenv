# dsenv

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dsenv)
![PyPI Downloads](https://img.shields.io/pypi/dm/dsenv)
![PyPI Version](https://img.shields.io/pypi/v/dsenv)
![GitHub Stars](https://img.shields.io/github/stars/marcinn/dsenv)
![License](https://img.shields.io/github/license/marcinn/dsenv)

Damn Simple Environment Variables loader for Python.
Supports Python 3.7 and newer.

## Install

```bash
pip install dsenv
```

## Usage

```python
from dsenv import load_env

# Load from ~/.env
load_env()

# Load from a custom path
load_env("./.env", override_env=False)
```

## Supported .env Syntax

- `KEY=VALUE`
- `export KEY=VALUE`
- `KEY="VALUE"` or `KEY='VALUE'`
- Comments with `#` on empty lines or after unquoted values

## Tests

```bash
pytest
```

Or use tox (if you have multiple Python versions installed):

```bash
tox
```

## TODO

- Add more parser behavior tests (especially edge cases) before changing parsing rules.
- Expand support for escape sequences in quoted values (starting with double quotes).
- Refine comment parsing edge cases (quoted vs unquoted values, `#` handling).
- Evaluate multiline values support.
- Evaluate variable interpolation support.

## License

BSD-3
