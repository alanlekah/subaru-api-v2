current_dir = $(shell pwd)

all: clean deploy

init:
	python3.6 -m venv venv
	venv/bin/pip3 install -r requirements.txt
	venv/bin/python3 -m zappa init

deploy:
	venv/bin/python3 -m zappa deploy dev

update:
	venv/bin/python3 -m zappa update dev