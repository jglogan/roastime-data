#! /bin/bash -e

#
#  Set up a Python virtual environment using pip-tools.
#
venv_name="${1:-gneiss-env}"

#
#  Create the virtual environment and activate it.
#
python3 -m venv "${venv_name}"
. "${venv_name}/bin/activate"

#
#  Install the basic things we need for pip-compile
#  to run smoothly, and then use it to generate
#  requirements.txt if one does not exist already.
#
python3 -m pip install --upgrade pip wheel pip-tools
if [ ! -f requirements.txt ] ; then
    pip-compile requirements.in > requirements.txt || rm -f requirements.txt
fi

#
#  Install all other packages from the locked
#  configuration.
#
pip3 install -r requirements.txt
