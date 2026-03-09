# Download Alpine latest
FROM alpine:3.11

# Fill image descriptors
LABEL maintainer="lesinsky@benderrobotics.com"

# Prepare image itself, this is in one step to minimize image size
RUN apk update --no-cache && \
    # Install necessary Alpine packages
    apk add --no-cache linux-headers gcc libc-dev eudev-dev python3 python3-dev py3-pip libusb-dev make && \
    # Prepare filesystem
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip && \
    # Install necessary Python packages, both of these should be added to pyproject.toml in build section.
    pip install --no-cache-dir wheel Cython
