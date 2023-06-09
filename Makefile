format:
	black .
	isort --profile black .

lint:
	flake8 --ignore=E203,E501,W503
	isort --check-only --profile black .
	black --check .

watch:
	find templates -type f -name '*.ts' | entr -s './ts_generate_js.sh'
