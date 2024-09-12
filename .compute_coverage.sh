#!/bin/bash

set -e

first_file_executed=false

for file in tests/*.py; do
    echo "FILE: $file"
    if [ -f "$file" ]; then
    	if [ "$first_file_executed" = false ]; then
        	python3 -m coverage run "$file" 1> /dev/null
		first_file_executed=true
	else
        	python3 -m coverage run -a "$file" 1> /dev/null
	fi

    fi
done

echo "COMPUTING COVERAGE REPORT"
python3 -m coverage report | grep TOTAL | sed "s/.* //"
echo "(To see full report: python3 -m coverage html)" >&2
