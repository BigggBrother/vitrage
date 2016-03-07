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

import abc
from collections import namedtuple
import six


ActionStepWrapper = namedtuple('ActionStepWrapper', ['type', 'params'])


EVALUATOR_EVENT_TYPE = 'type'


@six.add_metaclass(abc.ABCMeta)
class Recipe(object):

    @staticmethod
    @abc.abstractmethod
    def get_do_recipe(params):
        """Execute the action.

        :param params: parameters of the action
        :type params: ActionSpecs
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_undo_recipe(params):
        """Undo the action.

        :param params: parameters of the action
        :type params: ActionSpecs
        """
        pass
