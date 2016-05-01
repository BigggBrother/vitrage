#!/usr/bin/env bash
# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

(cd $BASE/new/vitrage/; sudo virtualenv .venv)
source $BASE/new/vitrage/.venv/bin/activate

sudo pip install nose

(cd $BASE/new/vitrage/; sudo pip install -r requirements.txt -r test-requirements.txt)
(cd $BASE/new/vitrage/; sudo python setup.py install)

(cd $BASE/new/vitrage/; sudo rm -rf .testrepository/)
(cd $BASE/new/vitrage/; sudo testr init)

(cd $BASE/new/vitrage/; sudo sh -c 'testr list-tests vitrage_tempest_tests | grep vitrage > vitrage_tempest_tests.list')
(cd $BASE/new/vitrage/; sudo sh -c 'testr run --subunit --load-list=vitrage_tempest_tests.list | subunit-trace --fails')
