#!/bin/bash

templates_dir=templates

tsc --strict --target es2017 --outDir $templates_dir/ts_output/js $(find $templates_dir -type f -name '*.ts');

docker-compose exec app python3 manage.py collectstatic --noinput
