#!/bin/bash
cd /src
git pull
#pip install -e .
python setup.py sdist upload -r internal
