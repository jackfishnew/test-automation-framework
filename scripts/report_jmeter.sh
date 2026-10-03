#!/usr/bin/env bash
apache-jmeter-5.6.3/bin/jmeter -g "tests/jmeter-report/kpi.jtl" -o tests/jmeter-report/html
python3 -m http.server 8001 --directory ./tests/jmeter-report