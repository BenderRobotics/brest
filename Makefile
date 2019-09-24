
.PHONY: all target clean install uninstall reinstall

TARGET:=dist/brest*.whl

all: $(TARGET)

$(TARGET):
	python setup.py bdist_wheel

clean:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf docs/_build

install: $(TARGET)
	pip install --user dist/*.whl

uninstall:
	pip uninstall brest -y

reinstall: uninstall clean install