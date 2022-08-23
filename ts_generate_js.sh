#!/bin/bash

templates_dir=templates

for i in $(find $templates_dir -type f -name '*.ts');
do
  tsc "$i" --strict --target es2017 --outDir $templates_dir/ts_output/js
done

docker-compose exec app python3 manage.py collectstatic --noinput

