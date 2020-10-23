# See LICENSE file for licensing details.

import unittest

from ops.testing import Harness
from charm import GrafanaK8s

BASE_CONFIG = {
    'advertised_port': 3000,
    'grafana_image_path': 'grafana/grafana:latest',
    'grafana_image_username': '',
    'grafana_image_password': '',
    'provisioning_path': '/etc/grafana/provisioning',
}


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(GrafanaK8s)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test__image_details_in_pod_spec(self):
        """Test whether image details come from config properly."""

        # basic setup
        self.harness.set_leader(True)
        self.harness.update_config(BASE_CONFIG)

        # emit the "config_changed" event and get pod spec
        self.harness.charm.on.config_changed.emit()
        pod_spec, _ = self.harness.get_pod_spec()

        # test image details
        expected_image_details = {
            'imagePath': 'grafana/grafana:latest',
        }

        self.assertEqual(expected_image_details,
                         pod_spec['containers'][0]['imageDetails'])
