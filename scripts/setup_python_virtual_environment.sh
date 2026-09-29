#!/usr/bin/env bash
python3 -m venv tests/venv
source tests/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt