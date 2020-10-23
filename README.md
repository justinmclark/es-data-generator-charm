# elasticsearch-data-provider

## Description

This charm is meant only to test the [Elasticsearch Operator charm](https://github.com/canonical/elasticsearch-operator/tree/develop). It will operate a container that generates random data for some period of time and then just wait in a loop (this is so users don't inadvertently add more data to ES than the host system(s) can handle).

Application source repository: https://github.com/justinmclark/elasticsearch-test-data

## Usage

Get the proper charm repos on your machine

```
# elasticsearch-operator is under active development, use the "develop" branch for most recent updates
git clone git@github.com:canonical/elasticsearch-operator.git
git clone git@github.com:justinmclark/es-data-generator-charm.git
```

Install dependencies

```
snap install juju --classic
snap install microk8s --classic
microk8s.enable dns storage
```

Setup your Juju environment

```
juju bootstrap microk8s mk8s
juju add-model lma
juju create-storage-pool operator-storage kubernetes storage-class=microk8s-hostpath
cd {PATH_TO_ES_OPERATOR_DIR} && charmcraft build && juju deploy ./elasticsearch-operator.charm
cd {PATH_TO_ES_DATA_PROVIDER_DIR} && charmcraft build && juju deploy ./es-data-provider.charm

# consider making Elasticsearch HA
juju add-unit -n2 elasticsearch-operator

# wait for all units/pods to be active
juju status --color
microk8s.kubectl get all -n lma

# add the relation and check out the data being inserted into the ES cluster
juju add-relation elasticsearch-operator es-data-provider

# find ES_APP_ADDRESS via juju status and ES_HTTP_PORT defaults to 9200 and is defined in the ES operator config
curl -X GET "{ES_APP_ADDRESS}:{ES_HTTP_PORT}/_stats?pretty"
```
