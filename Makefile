format:
	black .
	isort --profile black .

lint:
	flake8 --ignore=E203,E501,W503 --exclude venv
	isort --check-only --profile black .
	black --check .

watch:
	npm run dev
