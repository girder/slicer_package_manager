FROM girder/girder:latest
MAINTAINER Kitware, Inc. <kitware@kitware.com>

RUN pip install girder-client ansible
RUN ansible-galaxy install girder.girder

WORKDIR /girder
COPY entrypoint.sh entrypoint.sh
COPY init.yml init.yml
COPY inventory /etc/ansible/hosts

ENTRYPOINT ["bash", "/girder/entrypoint.sh"]
