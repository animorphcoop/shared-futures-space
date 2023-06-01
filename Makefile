format:
	black --exclude '/\.venv/' .
	isort --profile black .

lint:
	isort --check-only --profile black .
	black --check --exclude '/\.venv/' .
