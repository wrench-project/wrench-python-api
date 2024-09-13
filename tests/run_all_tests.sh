#!/bin/bash

set -e

for file in *.py; do
    if [ -f "$file" ]; then
      	python3 "$file" 1> /dev/null
	if [ $? -eq 0 ]; then
  		echo "$file [PASSED]"
	else
  		echo "$file [FAILED]"
	fi      	
    fi
done

