##
# Copyright (2016) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

import unittest
import mock

from hpOneView.oneview_client import OneViewClient
from oneview_enclosure_env_config_facts import EnclosureEnvConfigFactsModule
from oneview_enclosure_env_config_facts import ENCLOSURE_NOT_FOUND

ERROR_MSG = 'Fake message error'

PARAMS_GET_BY_NAME = dict(
    config='config.json',
    name="Test-Enclosure"
)

PRESENT_ENCLOSURES = [{
    "name": "Test-Enclosure",
    "uri": "/rest/enclosures/c6bf9af9-48e7-4236-b08a-77684dc258a5"
}]

ENVIRONMENTAL_CONFIGURATION = {
    "calibratedMaxPower": "2500"
}


def create_ansible_mock(params):
    mock_params = mock.Mock()
    mock_params.__getitem__ = mock.Mock(side_effect=lambda name: params[name])

    mock_ansible = mock.Mock()
    mock_ansible.params = mock_params
    return mock_ansible


class EnclosureEnvConfigFactsSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_enclosure_env_config_facts.AnsibleModule')
    def test_should_get_environmental_configuration(self, mock_ansible_module,
                                                    mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.enclosures.get_by.return_value = PRESENT_ENCLOSURES
        mock_ov_instance.enclosures.get_environmental_configuration.return_value = ENVIRONMENTAL_CONFIGURATION

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        EnclosureEnvConfigFactsModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(enclosure_env_config=ENVIRONMENTAL_CONFIGURATION)
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_enclosure_env_config_facts.AnsibleModule')
    def test_should_fail_when_get_env_config_raises_error(self, mock_ansible_module,
                                                          mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.enclosures.get_by.return_value = PRESENT_ENCLOSURES
        mock_ov_instance.enclosures.get_environmental_configuration.side_effect = Exception(ERROR_MSG)

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        EnclosureEnvConfigFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once()

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_enclosure_env_config_facts.AnsibleModule')
    def test_should_fail_when_get_by_name_raises_error(self,
                                                       mock_ansible_module,
                                                       mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.enclosures.get_by.side_effect = Exception(ERROR_MSG)
        mock_ov_instance.enclosures.get_environmental_configuration.return_value = None

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        EnclosureEnvConfigFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once()

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_enclosure_env_config_facts.AnsibleModule')
    def test_should_do_nothing_when_enclosure_not_exist(self,
                                                        mock_ansible_module,
                                                        mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.enclosures.get_by.return_value = []
        mock_ov_instance.enclosures.get_environmental_configuration.return_value = None

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        EnclosureEnvConfigFactsModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(enclosure_env_config=None),
            msg=ENCLOSURE_NOT_FOUND)


if __name__ == '__main__':
    unittest.main()
