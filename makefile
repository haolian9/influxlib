freeze_as_requirements:
	@ poetry export --format requirements.txt --without-hashes > requirements.txt

install:
	@ python3 -m venv venv
	@ venv/bin/pip install -r requirements.txt

