#!/usr/bin/env bash

allure generate tests/allure-report -o allure-report --clean
python3 -m http.server 8001 --directory allure-report