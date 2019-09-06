
.PHONY: all target clean install uninstall reinstall

TARGET:=brest*.whl

all: $(TARGET)

$(TARGET):
	python setup.py bdist_wheel

clean:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm =rf docs/_build

install: $(TARGET)
	pip install dist/*.whl

uninstall:
	pip uninstall brest -y

reinstall: uninstall clean install