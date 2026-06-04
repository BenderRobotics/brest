<div align="center">
<img alt="pdoc" src="./docs/_static/logo.svg" width="320" />
</div>
</br>

# Bender Robotics Embedded Systems Toolkit
Goal of the Brest project is to provide a python based resource manager and common libraries for embedded system testing.

If you are looking for the **documentation**, please refer [here](https://docs.benderrobotics.com/brest/) or [build offline](docs/README.md#building-the-offline-documentation).


## Install Brest
    $ pip install brest

## Installing Brest from the source
    $ pip install https+git://github.com/BenderRobotics/brest.git

## Optional Modules
    $ pip install "brest[<module>]"

Available modules: [cameras_win, cameras_unix, jlink_win]

## Minimal Example
See [minimal example files](examples/minimal_example/example.py)
```yaml
# project_config.yaml - define what project needs
project_name:
    psu:
        class_name: 'Supplies'
        disable_on_destruct: False
        default:
            voltage: 12
            current: 0.5
```
```yaml
# user_config.yaml - alter specific instance at end-setup
project_name:
    psu:
        class_name: 'Supplies.ManSup'
```
```py
# example.py
# Simple example showing operation with power supply.
import brest

resources = brest.Resources("project_name", "user_config.yaml", "project_config.yaml", needed=["psu"])
psu = resources["psu"]

print(psu.voltage)
psu.voltage = psu.voltage * 2
psu.enable()
```
See other [examples](examples/)

## Branching strategy
Because Brest is a relatively small project, it uses a very basic branching strategy.
All feature branches keep their history and merge into the 'devel' branch as merge-commits.
If there has been a commit in the 'devel' branch while the feature branch was under development,
the procedure is to merge 'devel' into the feature branch (as a merge-commit) to update changes and when the feature
branch development is over, it can be merged with 'devel'.

