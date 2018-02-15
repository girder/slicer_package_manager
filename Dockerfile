# To build the image:
#
#  docker build -t girder/slicer_extension_manager:web .
#
# To shell inside the image:
#
#  docker run -ti --entrypoint bash --rm  girder/slicer_extension_manager:web
#
# To shell inside the container
#
#  docker exec -ti $(docker-compose ps -q NAME) /bin/bash
#
FROM girder/girder:latest
MAINTAINER Kitware, Inc. <kitware@kitware.com>

RUN pip install girder-client ansible
RUN ansible-galaxy install girder.girder

COPY server /girder/plugins/slicer_extension_manager/server/
COPY web_client /girder/plugins/slicer_extension_manager/web_client/
COPY web_external /girder/plugins/slicer_extension_manager/web_external/
COPY plugin.cmake /girder/plugins/slicer_extension_manager/
COPY plugin.json /girder/plugins/slicer_extension_manager/
COPY README.md /girder/plugins/slicer_extension_manager/

RUN girder-install web --dev --plugins slicer_extension_manager
