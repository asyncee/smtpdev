bootstrap:
	rm -rf ./env
	virtualenv -p python3 env
	env/bin/pip install -e .

run:
	python server.py
