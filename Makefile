format:
	black .
	isort --profile black .

lint:
	isort --check-only --profile black .
	black --check .
	flake8 --ignore=E203,E501,W503
