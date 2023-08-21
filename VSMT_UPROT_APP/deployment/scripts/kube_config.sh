#!/usr/bin/env bash

# Fail on error
set -e

ENV=${1?You must pass in the env you are deploying to i.e live-lk8s-nonprod or live-lk8s-prod}

if [[ ${ENV} == 'live-lk8s-nonprod' ]]; then
  BUCKET="nhsd-texasplatform-kubeconfig-lk8s-nonprod"
  FILE="live-leks-cluster_kubeconfig"
elif [[ ${ENV} == 'live-lk8s-prod' ]]; then
  BUCKET="nhsd-texasplatform-kubeconfig-lk8s-prod"
  FILE="live-leks-cluster_kubeconfig"
elif [[ ${ENV} == 'live-mgmt' ]]; then
  BUCKET="nhsd-texasplatform-kube-config-mgmt-devtools"
  FILE="live-mgmt-leks-cluster_kubeconfig"
elif [[ ${ENV} == 'test-lk8s' ]]; then
  BUCKET="nhsd-texastest-kube-config-lk8s"
  FILE="test-leks-cluster_kubeconfig"
elif [[ ${ENV} == 'test-mgmt' ]]; then
  BUCKET="nhsd-texastest-kube-config-mgmt-devtools"
  FILE="test-mgmt-leks-cluster_kubeconfig"
elif [[ ${ENV} == 'dev-lk8s' ]]; then
  BUCKET="nhsd-texasdev-kube-config-lk8s"
  FILE="dev-leks-cluster_kubeconfig"
elif [[ ${ENV} == 'dev-mgmt' ]]; then
  BUCKET="nhsd-texasdev-kube-config-mgmt-devtools"
  FILE="dev-mgmt-leks-cluster_kubeconfig"
else
  echo "Invalid env name ${ENV}"
  exit 1
fi

aws s3 cp s3://${BUCKET}/${FILE} ${WORKSPACE}/${FILE} --source-region=eu-west-2 --region=eu-west-2 2>&1 >/dev/null

echo "${WORKSPACE}/${FILE}"
