# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test example app."""

import json
import os
import signal
import subprocess
import time

import pytest


@pytest.yield_fixture
def example_app():
    """Example app fixture."""
    current_dir = os.getcwd()

    # Go to example directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exampleappdir = os.path.join(project_dir, "examples")
    os.chdir(exampleappdir)

    # Setup example
    cmd = "./app-setup.sh"
    exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

    # Starting example web app
    cmd = "python app.py"
    webapp = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, preexec_fn=os.setsid, shell=True
    )
    time.sleep(10)
    # Return webapp
    yield webapp

    # Stop server
    try:
        os.killpg(webapp.pid, signal.SIGTERM)
    except OSError as err:
        print(f"ERROR stop server: {webapp.pid}")
        os.system(f"sudo kill {webapp.pid}")

    # Tear down example app
    cmd = "./app-teardown.sh"
    subprocess.call(cmd, shell=True)

    # Return to the original directory
    os.chdir(current_dir)
    cmd = "pip install -e .[all]"
    subprocess.call(cmd, shell=True)


def test_example_app(example_app):
    """Test example app."""
    cmd = "curl http://localhost:5000/schemas/biology/animal_record_schema.json"
    output = json.loads(subprocess.check_output(cmd, shell=True).decode("utf-8"))
    assert (
        output["id"]
        == "http://localhost:5000/schemas/biology/animal_record_schema.json"
    )
    allof = output["allOf"]
    assert len(allof) == 2
    for obj in allof:
        if "$ref" in obj:
            assert obj["$ref"] == "http://localhost:5000/schemas/record_schema.json"
        if "properties" in obj:
            assert allof[1]["properties"]["specie"]["type"] == "string"
            assert allof[1]["type"] == "object"

    cmd = "curl http://localhost:5000/schemas/record_schema.json"
    output = json.loads(subprocess.check_output(cmd, shell=True).decode("utf-8"))
    assert output["id"] == "http://localhost:5000/schemas/record_schema.json"
    assert output["type"] == "object"
    assert output["properties"]["title"]["type"] == "string"
