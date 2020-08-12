# To build the image:
#
#  docker build -t girder/slicer_package_manager:web .
#
# To shell inside the image:
#
#  docker run -ti --entrypoint bash --rm  girder/slicer_package_manager:web
#
# To shell inside the container
#
#  docker exec -ti $(docker-compose ps -q NAME) /bin/bash
#
FROM girder/girder:3.1.0-py3
MAINTAINER Kitware, Inc. <kitware@kitware.com>

RUN pip install girder-client ansible
RUN ansible-galaxy install girder.girder

COPY MANIFEST.in /slicer_package_manager/MANIFEST.in
COPY README.rst /slicer_package_manager/README.rst
COPY setup.cfg /slicer_package_manager/setup.cfg
COPY setup.py /slicer_package_manager/setup.py
COPY slicer_package_manager /slicer_package_manager/slicer_package_manager

RUN pip install /slicer_package_manager

RUN girder build
