#!/bin/sh

set -e

for file in */simulator.py; do
	echo "*** RUNNING EXAMPLE $file ***"
	python3 $file
done
