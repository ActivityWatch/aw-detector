.PHONY: build test

build:
	python3 setup.py install

test:
	./scripts/typecheck.sh

package:
	true
