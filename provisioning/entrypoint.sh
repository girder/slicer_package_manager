#!/usr/bin/env bash

cd /girder
pip install -e '.[plugins]'

vars="ghost=$GIRDER_HOST"
vars="$vars gport=$GIRDER_PORT"
vars="$vars admin_name=$GIRDER_ADMIN_NAME"
vars="$vars admin_pass=$GIRDER_ADMIN_PASS"

export ANSIBLE_LIBRARY=/root/.ansible/roles/girder.girder/library

echo "RUNNING CONFIGURATION"
ansible-playbook -v --extra-vars "$vars" init.yml
echo "CONFIGURATION COMPLETE"

echo "SLEEPING"
while true ; do
    sleep 600
done
