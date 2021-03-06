# Copyright 2016 - Alcatel-Lucent
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

from oslo_config import cfg


# Register options for the service
OPTS = [
    cfg.StrOpt('templates_dir',
               default='/etc/vitrage/templates',
               help='A path for the templates used by the evaluator'
               ),
    cfg.StrOpt('equivalences_dir',
               default='/etc/vitrage/templates/equivalences',
               help='A path for entity equivalences used by the evaluator'
               ),
    cfg.StrOpt('def_templates_dir',
               default='/etc/vitrage/templates/def_templates',
               help='A path for def_template templates used by the evaluator'
               ),
    cfg.IntOpt('workers',
               default=None,
               min=1,
               max=32,
               help='Number of workers for template evaluator, default is '
                    'equal to the number of CPUs available if that can be '
                    'determined, else a default worker count of 1 is returned.'
               ),
]
