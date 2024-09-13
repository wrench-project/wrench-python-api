#!/bin/sh

set -e

for file in */*.py; do
	echo "*** RUNNING EXAMPLE $file ***"
	python3 $file
done
