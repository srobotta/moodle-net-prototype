## Export MoodleNet Resources

This directory contains a stand alone script to export resources that are in the MoodleNet
database.

The idea of the script was to get out our data from the existing MoodleNet installation
and import it in another platform (we have choosen https://oer.switch.ch/). The import is
done via some CSV upload.

### Setup

Before starting to export the data with the `export.py` script you need to have python
installed.

Requirements:

* Python 3.x
* python-arango package (install via pip: pip install python-arango)
* python-slugify package (install via pip: pip install python-slugify)

Also before you start, the MoodleNet configuration must be fetched from your installation.
To make things easy you may just copy the `default.config.json` from MoodleNet and use
it for the `export.py` script. Credentials may also be provided manually.

Finally, there must be a database connection available to your MoodleNet installation.
I use the command `ssh -NL 8529:localhost:8529 user@moodlenet.server` from the 
[tweaks.md](../tweaks.md) to enable port forwarding from my local machine to the ArangoDB
of the MoodleNet installation. The database server would then be localhost.

### Export data

This script reads from a MoodleNet ArangoDB database all resources and
exports them in the desired output format e.g. Switch OER CSV. There are also some
command line arguments to fetch a single resource and display it on the console (e.g.
JSON). Also, to get an overview, a list of resources with their ID and title can
be printed.

An documentation of the `export.py` script is included in the script and can be
invoked with `python export.py --help`.

The module name for Switch OER is in the file `switchoer.py` and imported dynamically
depending on the format invoked  with the `-e switch-oer` argument. The export script
can be easily exported by some custom module. A minimal implementation is contained
in `xml.py` which exports a very simple XML file (just for demonstration purposes).

The document from the database is fetched via `getMnetResource()` in the export
script and returns a `MoodleNetResource`. This instance together with the
other modles in `moodlenet.py` represents a complete MoodleNet resource.

There might be some bugs that I didn't address. Feel free to report an issue or
pull request. 