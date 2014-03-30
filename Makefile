.PHONY: clean test test-unit test-integration

clean-pyc:
	echo 'Cleaning .pyc files'
	$(shell find * -name "*.pyc" | xargs rm -rf)

clean: clean-pyc

test: clean
	coverage run --source tictail -m py.test -s
	coverage report -m