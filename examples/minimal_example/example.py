# Simple example showing operation with power supply.
import brest

resources = brest.Resources("project_name", "user_config.yaml", "project_config.yaml", needed=["psu"])
psu = resources["psu"]

print(psu.voltage)
psu.voltage = psu.voltage * 2
psu.enable()
