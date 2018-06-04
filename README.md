# perch-client
A CLI for Perch Security


## Requirements
- Python 2.7+ or Python 3


## Installation
- `pip install perch`

## Usage
- Create a CSV file with your indicators in [this format](https://docs.google.com/spreadsheets/d/1Il8YP3P-1_amA2nTXU14sLPy1fs6kzfLgjxb73WHJ20)
- `perch upload_indicators_csv <path-to-csv>`


## Development
- Create a virtual env for the project `python3 -m venv /path/to/new/virtual/environment`
- Sym link the `activate` script created at `/path/to/new/virtual/environment/bin` to the project folder
- Add `export PERCH_ENV="DEV"` to the `activate` script. You could also set this to `QA` if you want to point at the QA server.
- `pip uninstall perch` then `pip install -e .` enables the `perch` command in your dev environment.

## Build and Release
- `python setup.py bdist_wheel`
- `twine upload dist/*`
