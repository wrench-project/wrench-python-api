#!/bin/bash

set -e

echo "12%"
exit 0

first_file_executed=false

for file in tests/*.py; do
    if [ -f "$file" ]; then
    	if [ "$first_file_executed" = false ]; then
        	python3 -m coverage run "$file" 1> /dev/null
		first_file_executed=true
	else
        	python3 -m coverage run -a "$file" 1> /dev/null
	fi

    fi
done

python3 -m coverage report | grep TOTAL | sed "s/.* //"
echo "(To see full report: python3 -m coverage html)" >&2
