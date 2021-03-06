# Copyright 2017 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

from oslo_log import log
from oslo_service import service as os_service
from vitrage.cli import VITRAGE_TITLE
from vitrage.persistor.service import PersistorService
from vitrage import service
from vitrage import storage

LOG = log.getLogger(__name__)


def main():
    print(VITRAGE_TITLE)
    conf = service.prepare_service()
    db_connection = storage.get_connection_from_config(conf)
    launcher = os_service.ServiceLauncher(conf)
    launcher.launch_service(PersistorService(conf, db_connection))
    launcher.wait()


if __name__ == "__main__":
    sys.exit(main())
