
.PHONY: all target clean install uninstall reinstall

TARGET:=brest*.whl

all: $(TARGET)

$(TARGET):
	python setup.py bdist_wheel
	mv dist/brest*.whl .

clean:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf *.whl

install: $(TARGET)
	pip install *.whl

uninstall:
	pip uninstall brest -y

reinstall: uninstall clean install