#!/usr/bin/env bash
sudo apt install python3.14-venv
python3 -m venv tests/venv
source tests/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt