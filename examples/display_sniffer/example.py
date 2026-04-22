"""
Example file for a usage of Display Sniffer in Brest.

Required hardware:  CYUSB3KIT-003 evaluation board
You might need to set up a few things for the Display Sniffer package,
please follow the instructions here:
https://gitlab.benderrobotics.com/br/tools/display-sniffer/-/tree/master/sw?ref_type=heads#-display-sniffer
"""

import brest
import cv2
import matplotlib.pyplot as plt

# Load the resources from the corresponding config file
resources = brest.Resources("project1", "./display_sniffer_config.yaml", needed=["cam"])

# Load the camera and print out its info
camera = resources["cam"]
info = camera.get_info()
print(info)


# Acquire image (numpy array)
np_image = camera.acquire_image()

# Show acquired image using cv2
cv2.imshow("frame", np_image)
key = cv2.waitKey(1000)

# Acquire single numpy image and show it using matplotlib
image = camera.acquire_image()
plt.imshow(image)
# hold the window
plt.waitforbuttonpress()
plt.close("all")
