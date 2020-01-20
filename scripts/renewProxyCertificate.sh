#!/bin/bash
# renew the proxy certificate if proxy duration is less than $1 minutes

if [ -z "${X509_USER_PROXY}" ]; then
    echo "ERROR: Please export the proxy location to X509_USER_PROXY"
    echo "Run export X509_USER_PROXY=$HOME/private/.proxy"
    exit
fi

if [ -z "${cmssw}" ]; then
    cmssw="10_2_18"
fi

module load singularity/3.4.1
singularity exec /mnt/hephy/cms/test/cmssw_CMSSW_${cmssw}.sif python -c 'import os; from proxyHelper import renew_proxy; renew_proxy(filename=os.getenv("X509_USER_PROXY"),request_time=192,min_time=os.getenv("min_proxyTime"))'
