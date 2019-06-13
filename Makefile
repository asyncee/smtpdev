bootstrap:
	rm -rf ./env
	virtualenv -p python3 env
	env/bin/pip install -r requirements-dev.txt

run:
	smtpdev --develop

check:
	mypy smtpdev --ignore-missing-imports

upload:
	rm -rf ./dist/*
	python setup.py sdist
	twine upload dist/*

docker-build:
	docker build -t smtpdev:latest .

docker-sh:
	docker run -it --rm smtpdev:latest /bin/sh

docker-run:
	docker run -it -p 2500:2500 -p 8080:8080 smtpdev:latest
