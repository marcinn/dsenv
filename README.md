# dsenv

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dsenv)
![PyPI Downloads](https://img.shields.io/pypi/dm/dsenv)
![PyPI Version](https://img.shields.io/pypi/v/dsenv)
![GitHub Stars](https://img.shields.io/github/stars/marcinn/dsenv)
![License](https://img.shields.io/github/license/marcinn/dsenv)

Damn Simple Environment Variables loader.

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
load_env("./.env", override=False)
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

## License

BSD-3
