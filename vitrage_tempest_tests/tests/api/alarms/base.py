# Copyright 2016 Nokia
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from vitrage.datasources.aodh.properties import AodhProperties as AodhProps
from vitrage_tempest_tests.tests.base import BaseVitrageTempest
from vitrage_tempest_tests.tests.common.tempest_clients import TempestClients


TEMPLATES_RESOURCES_PATH = 'resources/templates/'
TEMPLATES_SOURCES_PATH = '/etc/vitrage/templates/'


class BaseAlarmsTest(BaseVitrageTempest):
    """Topology test class for Vitrage API tests."""

    @classmethod
    def setUpClass(cls):
        super(BaseAlarmsTest, cls).setUpClass()

    def _check_num_alarms(self, num_alarms=0, state=''):
        if len(TempestClients.aodh().alarm.list()) != num_alarms:
            return False

        return all(alarm[AodhProps.STATE].upper() == state.upper()
                   for alarm in TempestClients.aodh().alarm.list())
