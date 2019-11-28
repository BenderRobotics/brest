# Download Alpine latest
FROM alpine:latest

# Fill image descriptors
LABEL maintainer="lesinsky@benderrobotics.com"
LABEL build_date="2019-11-28"

# Install necessary Alpine packages
RUN apk update
RUN apk add linux-headers gcc libc-dev eudev-dev python3 python3-dev libusb-dev make

# Prepare filesystem
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

# Install necessary Python packages
RUN pip install wheel
