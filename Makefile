all: format.html

format.html: format.rst
	rst2html.py $? > $@

samples:
	cd samples; python generate.py

clean:
	rm -f format.html samples/*.akaibu

.PHONY: clean samples
