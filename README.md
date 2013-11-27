# Pyphant

Pyphant is a framework for scientific data analysis. It features a
flexible plugin architecture allowing for the application in many
different fields.

This repository includes the python packages pyphant and the toolboxes

* fmfile
* ImageProcessing
* OSC
* Statistics
* tools

## Installation

Pyphant runs with python 2.6 or python 2.7

### Dependencies

Some of pyphant's dependencies may not work with the common python
package managers and have to be installed manually.
Here is a complete list of the python packages required by pyphant and
its toolboxes:

* sogl
* paste
* simplejson
* matplotlib
* numpy
* scipy
* tables
* wxPython
* egenix-mx-base
* configobj
* PIL

### Linux

#### Using *easy_install*

To install the latest stable version from PyPI:

    $ easy_install pyphant

The toolboxes can be installed by

    $ easy_install pyphant.fmf
    $ easy_install pyphant.imageprocessing
    $ easy_install pyphant.osc
    $ easy_install pyphant.statistics
    $ easy_install pyphant.tools

For more information like installation locations etc. consider

    $ easy_install --help

#### Installation from source

To install the latest (unstable) version from source:

    $ git clone https://github.com/SGWissInfo/pyphant1.git
    $ cd pyphant1/src/pyphant
    $ python setup.py develop

Also consider

    $ python setup.py --help

for more options. You may also want to comment out some of the
dependencies in the *setup.py* file and install them manually
e.g. from your system's package manager.

The toolboxes each have their own *setup.py* script which is located
in *src/workers/$TOOLBOX_NAME*.

### OS X

Stable versions of pyphant and the toolboxes are available as
[macports](http://www.macports.org/) packages.

You may also want to install from source as described in the *Linux* section.

### Windows

A custom installer for Windows is not yet available.
Please follow the *Installation from source* analogously as described in the
*Linux* section. You will have to install the dependencies first or
setup an environment that allows to compile the needed dependencies.

## Graphical User Interface (GUI)

Pyphant comes with a GUI. Under Linux or Mac OS X it can be invoked
from a terminal after a succesfull installation by

    $ wxPyphant

If this command is not available on your platform, the GUI can also be
invoked by running
*src/pyphant/pyphant/wxgui2/wxPyphantApplication.py* with your python
interpreter.
