# REMS Copy
This tool can be used to copy licenses, forms, resources, workflows, catalogue items and categories from one [REMS](https://github.com/cscfi/rems) environment to another.

## Installation
```
git clone https://github.com/CSCfi/rems-copy
pip install .
```

## Usage
```
rems-copy
usage: rems-copy [-h] [-c CONFIG] [-l LANGUAGE]
               {licenses,forms,resources,workflows,catalogue,all} source
               destination

This tool copies REMS items from one instance to another

positional arguments:
  {licenses,forms,resources,workflows,catalogue,categories,all}
                        items to move
  source                source environment where items are downloaded from
  destination           destination environment where items are uploaded to

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to JSON configuration file,
                        default='./config.json'
  -l LANGUAGE, --language LANGUAGE
                        two letter language code, which is used for matching
                        item titles, default='en'
```

## Configuration
The tool is configured with a JSON file, an example file is given with [config.json](config.json).
```
{
    "demo": {
        "url": "https://rems-demo.rahtiapp.fi/",
        "key": "",
        "username": "",
        "organisation: ""
    },
    "test": {
        "url": "https://rems-test.rahtiapp.fi/",
        "key": "",
        "username": "",
        "organisation": ""
    }
}
```
When using the tool, the `source` and `destination` arguments refer to the object names highest in the structure, e.g. `demo` and `test`. More REMS instances can be freely added by adding more objects.

## Examples
### Action
```
rems-copy <items-to-copy> <from> <to> --config <path> --language <lang>
```
### Copy Licenses
```
rems-copy licenses demo test
```
### Copy Forms
```
rems-copy forms demo test
```
### Copy Resources
```
rems-copy resources demo test
```
### Copy Workflows
```
rems-copy workflows demo test
```
### Copy Catalogue Items
```
rems-copy catalogue demo test
```
### Copy Catalogue Items
```
rems-copy categories demo test
```
### Copy Everything
This command runs all of the commands above in the correct order.
```
rems-copy all demo test
```
## Order Matters
Order matters when copying items.
- Licenses are standalone
- Forms are standalone
- Resources depend on licenses
- Workflows depend on forms
- Catalogue items depend on forms, resources and workflows
- Categories depend on catalogue items

Copy dependencies of items first to avoid errors.
