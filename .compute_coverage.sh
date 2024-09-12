#!/bin/bash

set -e

first_file_executed=false

ls -la /home/wrench/

for file in tests/*.py; do
    echo "FILE: $file"
    if [ -f "$file" ]; then
    	if [ "$first_file_executed" = false ]; then
        	python3 -m coverage run --data-file=/tmp/.coverage "$file"
		first_file_executed=true
	else
        	python3 -m coverage run --data-file=/tmp/.coverage -a "$file"
	fi

    fi
done

echo "COMPUTING COVERAGE REPORT"
python3 -m coverage report --data-file=/tmp/.coverage | grep TOTAL | sed "s/.* //"
echo "(To see full report: python3 -m coverage html --data-file=/tmp/.coverage )" >&2
