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
- `pip install -e .` enables the cli

## Build and Release
- `python setup.py bdist_wheel`
- `twine upload dist/*`
