current_dir = $(shell pwd)

all: clean deploy

init:
	pipenv --python 3.6
	pipenv install
	pipenv run zappa init

deploy:
	pipenv run zappa deploy dev

update:
	pipenv run zappa update dev