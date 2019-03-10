#!/bin/bash

export FLASK_ENV=development

pip3 install -r requirements.txt

FLASK_APP=api.py flask run