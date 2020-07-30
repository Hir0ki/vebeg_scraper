#!/bin/bash

if [ -f "$PWD/.env" ]
then 
    export $(grep -v '^#' $PWD/.env | xargs)
elif [ -f "$PWD/.dev-env" ]
then
    export $(grep -v '^#' $PWD/.dev-env | xargs)
fi

exec python ./vebeg_scraper/main.py