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
