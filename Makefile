.PHONY: clean test

clean-pyc:
	echo 'Cleaning .pyc files'
	$(shell find * -name "*.pyc" | xargs rm -rf)

clean: clean-pyc

test: clean
	coverage run --source tictail -m py.test -s
	coverage report -m

test-unit: clean
	coverage run --source tictail -m py.test tests/unit -s
	coverage report -m

test-integration: clean
	coverage run --source tictail -m py.test tests/integration -s
	coverage report -m

test-travis: clean
	coverage run --source tictail -m py.test -s -m "not travis_race_condition"
	coverage report -m
