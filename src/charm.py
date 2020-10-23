#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import textwrap

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus

log = logging.getLogger()


class ESDataGenerator(CharmBase):
    store = StoredState()

    def __init__(self, *args):
        super().__init__(*args)

        # basic event observations
        self.framework.observe(self.on.config_changed, self.on_config_changed)
        self.framework.observe(self.on['elasticsearch'].relation_changed, self.on_es_changed)

        self.store.set_default(es_url='')

    def on_config_changed(self, event):
        self.configure_pod()

    def on_es_changed(self, event):
        log.warning('PROVIDER: on_es_changed event triggered.')
        
        log.error(event.relation.data[event.unit])
        port = event.relation.data[event.unit].get('port')
        ingress_address = event.relation.data[event.unit].get('ingress-address')
        
        if ingress_address is None or port is None:
            log.error('Do not have proper relation data passed by ES to es-data-provider')
            return
        
        log.warning('PROVIDER: es_url is being set. Data should be sent to ES.')
        self.store.es_url = 'http://{}:{}'.format(ingress_address, port)
        self.configure_pod()    

    def _build_pod_spec(self):
        """Builds the pod spec based on available info in datastore`."""
        log.warning('PROVIDER: building pod spec.')

        config = self.model.config

        # set image details based on what is defined in the charm configuation
        image_details = {
            'imagePath': config['es_data_gen_image_path']
        }

        spec = {
            'version': 3,
            'containers': [{
                'name': self.app.name,
                'imageDetails': image_details,
                'ports': [{
                    'containerPort': 9876,
                    'protocol': 'TCP',
                }],
                'envConfig': {
                    'ES_URL': self.store.es_url,
                },
            }]
        }

        return spec

    def configure_pod(self):
        """Set Juju / Kubernetes pod spec built from `_build_pod_spec()`."""

        # setting pod spec and associated logging
        if not self.unit.is_leader():
            self.unit.stats = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus('Building pod spec.')

        pod_spec = self._build_pod_spec()
        self.model.pod.set_spec(pod_spec)
        
        self.unit.status = ActiveStatus()
        log.warning('Pod spec set successfully.')


if __name__ == '__main__':
    main(ESDataGenerator)
