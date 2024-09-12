#!/bin/bash

set -e

for file in *.py; do
    if [ -f "$file" ]; then
      	python3 "$file"
    fi
done

