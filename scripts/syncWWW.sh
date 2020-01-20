#!/bin/bash

if [ -z "${CERN_USER}" ]; then
    echo "Please export your CERN user name to CERN_USER in adding the following lines to ~/.bash_profile"
    echo "CERN_USER=YOUR_CERN_USERNAME"
    echo "export CERN_USER"
    echo ""
    echo "Then run"
    echo "source ~/.bash_profile"
    echo ""
    echo "Create the directory /eos/user/YOUR_INITIAL/YOUR_CERN_USERNAME/www/ on lxplus"
    echo ""
    echo "Follow the steps of this website"
    echo "https://cernbox-manual.web.cern.ch/cernbox-manual/en/web/personal_website_content.html#create_personal_space"
    echo "to create a webpage and view your plots!"
else
    echo "Syncing the directory ${HOME}/www/ to /eos/user/$(echo ${CERN_USER} | head -c 1)/${CERN_USER}/www/"
    rsync -avuq ${HOME}/www/* ${CERN_USER}@lxplus.cern.ch:/eos/user/$(echo ${CERN_USER} | head -c 1)/${CERN_USER}/www/
fi

