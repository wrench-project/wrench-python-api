#!/bin/bash

BOLD=$(tput bold)
NORMAL=$(tput sgr0)
GREEN="\033[0;32m"
RED="\033[0;31m"

for file in *.py; do
    if [ -f "$file" ]; then
      	python3 "$file" 1> /dev/null 2> /tmp/stderr.txt
	if [ $? -eq 0 ]; then
  		echo -e "${BOLD}${GREEN}[PASSED] ${NORMAL}${BOLD}$file${NORMAL}"
	else
  		echo -e "${BOLD}${RED}[FAILED] ${NORMAL}${BOLD}$file${NORMAL}"
		cat /tmp/stderr.txt | sed 's/^/    /'
	fi      	
    fi
done

