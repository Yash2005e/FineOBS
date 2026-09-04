# What Broke and How We Got Out

During development, FineOBS encountered several integration and
environment issues.

## 1. Python package resolution

Problem:

The application failed to import backend packages when scripts
were executed directly.

Error:

`ModuleNotFoundError: No module named 'backend'`

Resolution:

We converted script execution to Python module execution:

```bash
python -m scripts.run_reconciliation