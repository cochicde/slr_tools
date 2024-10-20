# Overview

This tool is intended to help handling large amounts of scientific resources, specially for SLR (Systemaic Literature Reviews).
This large amount of resources needs to be reviewed and classified.
This tool allows to load all the metadata from scientific resources and store them in a database (sqlite3). 
A GUI allows later to fetch the data to easily classify it and/or add notes on it.

When classifying and all over the code, you will see `rejected` as an information about the resources. This a list of options that you would assign to the resources. In that list, you will have an option for a resource that should be accepted in your investigation,  which seems counter intuitive, but the `rejected` field is just a name given to the options to classify the resources. 

# How to use it

1. Install all needed packages

`pip install pybtex requests`

2. Run the example
- Query generator: `python3 ./slr.py query --query query.yml`
- Load resources into the database: `python3 ./slr.py load -d ./example/test.db -b ./example/bibtex.bib -c ./example/ieee.csv`
- Run the GUI: `python3 ./slr.py gui -c ./example/config-gui.yml`

# Commands

There are different tools in this repository:
- Generate query strings.
- Load scientific resources into a local database
- Run the GUI to handle the resources in the database

# Generate query strings

This tool allows generating search strings for different pages to be used, usually, in the advanced search. Supported pages are for now:
- Scopus 
- IEEE
- ACM

This tool requires an input `yml` file which tries to unify different search terms into a common format. 
A single query is compossed of: 
- operator: AND/OR
- terms: terms to look for
- fields: which fields to look for. Possible values
    - title
    - abstract
    - keywords
    - all
- negated: boolean indicating if the single query is negated or not

Single queries are group into `queries` which can also be negated and have an operator.

The `./example/query.yml` file offers an example of the following query:

```
(
  Programmable Logic Controller OR
  (
    PLC AND
    NOT Power Line Communications
  )
)
AND
(
  software OR
  program OR
  debug
)
```

## Execute command

`python3 ./slr.py query --query query.yml`

# Loading scientific resources

Initially, the tool was developed to automatically fetch all data directly from databases (ieee, scopus, ...), but this was too hard to maintain and not very much documentation is available on the remote side. The code is still there under `loader.remote` but it's not being mantained anymore. 

The best option is to load the data from files. `bibtex` and `ieee csv` files are supported. These are more common standard and much easier to maintain (see `loade.file`).

Once you do your search, you should export the results into one of these types of files.

## Execute command

You need a database where to load the resources (one will be created if it does not exist). Then you pass one or more csv files from ieee and/or one or more files in bibtex format.

`python3 ./slr.py load -d ./example/test.db -b ./example/bibtex.bib -c ./example/ieee.csv`

# Run GUI

You need to pass a configuration file in `yml` with the rejected options, the database name and an optional text to hightlight.

`python3 ./slr.py gui -c ./example/config-gui.yml` 

Use the left/right arrow to go to the next/previous scientific resource. Up/down will change the `rejected` value of the resource (or the number according to it can also be used). The `rejected` options you have in your configuration file are going to be loaded and shown on the right of the GUI with a shortcut for each one of them (provided you have less than 10).

Use `t` to start writing notes.

s` or `d` if you want to not save it or not for later.

Whenever you go to the next or previous resource, the changes are stored back in the database.
