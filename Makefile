build: build.stamp

venv: venv/touchfile

build.stamp: venv
	. venv/bin/activate; rm -rf fonts/; python3 process.py && touch build.stamp

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt

clean:
	rm -rf venv
	find . -name "*.pyc" -delete

update:
	pip install --upgrade $(dependency); pip freeze > requirements.txt
