#!/bin/bash

templates_dir=templates
echo $templates_dir
allfiles=$(find $templates_dir -type f -name '*.ts')

#declaring empty before loop
last_dir=""

for path in $allfiles
do
    dir_name=${path%/*}  # retain the part before the last slash so we pass files from the same dir
    if [[ "$dir_name" == "$last_dir" ]]; then
      echo "same dir"
    else
      if [[ "$last_dir" != "" ]]; then #to take out the first iteration
         echo "compiling from ${last_dir}" #compile from last dir
         tsc --strict --target es2017 --outDir $templates_dir/ts_output/js $(find $last_dir -type f -name '*.ts');
      fi
      last_dir=$dir_name
    fi
done

docker-compose exec app python3 manage.py collectstatic --noinput
