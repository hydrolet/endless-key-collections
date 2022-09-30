# endless-key-collections
The definition of the Endless Key content collections.

## Building the JSON files

To generate the JSON files from the INI files:
```
for INI_FILE in ini/*ini
  do ./tools/init2json.py $INI_FILE -o json/
  done
```

## Development

Setup pre-commit:

```
pipenv install --dev
pipenv run pre-commit install
```

In case you want to run the checks by hand you can do:

```
pipenv run pre-commit run --all-files
```
