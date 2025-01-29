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
FROM girder/girder:v3.2.8
MAINTAINER Kitware, Inc. <kitware@kitware.com>

RUN pip install girder-client ansible
RUN ansible-galaxy install girder.girder

COPY pyproject.toml /slicer_package_manager/pyproject.toml
COPY README.rst /slicer_package_manager/README.rst
COPY setup.py /slicer_package_manager/setup.py
COPY slicer_package_manager /slicer_package_manager/slicer_package_manager
COPY tests /slicer_package_manager/tests

RUN pip install /slicer_package_manager

RUN girder build
