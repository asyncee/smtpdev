bootstrap:
	rm -rf ./env
	virtualenv -p python3 env
	env/bin/pip install -r requirements.txt

run:
	python server.py
