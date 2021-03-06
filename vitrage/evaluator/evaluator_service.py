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

import multiprocessing
import time

from oslo_concurrency import processutils
from oslo_log import log
from oslo_service import service as os_service

from vitrage.entity_graph import EVALUATOR_TOPIC
from vitrage.evaluator.evaluator_base import EvaluatorBase

from vitrage.evaluator.scenario_evaluator import ScenarioEvaluator
from vitrage.evaluator.scenario_repository import ScenarioRepository
from vitrage.messaging import VitrageNotifier

LOG = log.getLogger(__name__)


START_EVALUATION = 'start_evaluation'
POISON_PILL = None


class EvaluatorManager(EvaluatorBase):

    def __init__(self, conf, entity_graph):
        super(EvaluatorManager, self).__init__(conf, entity_graph)
        self._workers_num = conf.evaluator.workers or \
            processutils.get_worker_count()
        self._worker_queues = list()
        self._p_launcher = os_service.ProcessLauncher(conf)

    def run_evaluator(self):
        LOG.info('Starting %s Evaluator Processes', str(self._workers_num))
        for i in range(self._workers_num):
            self._add_worker(enabled=False)
        self._notify_all(None, None, None, evaluator_action=START_EVALUATION)
        self._entity_graph.subscribe(self._notify_all)

    def _add_worker(self, enabled=False):
        """Create an EvaluatorWorker and it's task queue

        The new worker is initialized with a scenario repository
        that only contains a portion of the templates
        """
        scenario_repo = ScenarioRepository(
            self._conf,
            len(self._worker_queues),
            self._workers_num)
        tasks_queue = multiprocessing.JoinableQueue()
        w = EvaluatorWorker(
            self._conf,
            tasks_queue,
            self._entity_graph,
            scenario_repo,
            enabled)
        self._p_launcher.launch_service(w)
        self._worker_queues.append(tasks_queue)

    def _notify_all(self, before, current, is_vertex, *args, **kwargs):
        """Notify all workers

        This method is subscribed to entity graph changes.
        Per each change in the main entity graph, this method will notify
         each of the evaluators, causing them to update their own graph.
        """
        evaluator_action = kwargs.get('evaluator_action', None)
        self._notify_and_wait((before, current, is_vertex, evaluator_action))

    def _notify_and_wait(self, payload):
        for q in self._worker_queues:
            q.put(payload)
        time.sleep(0)  # context switch before join
        for q in self._worker_queues:
            q.join()

    def stop_all_workers(self):
        self._notify_and_wait(POISON_PILL)
        for q in self._worker_queues:
            q.close()
        self._worker_queues = list()

    def reload_all_workers(self, enabled=True):
        self.stop_all_workers()
        for i in range(self._workers_num):
            self._add_worker(enabled=enabled)


class EvaluatorWorker(os_service.Service):
    def __init__(self,
                 conf,
                 task_queue,
                 entity_graph,
                 scenario_repo,
                 enabled=False):
        super(EvaluatorWorker, self).__init__()
        self._conf = conf
        self._task_queue = task_queue
        self._entity_graph = entity_graph
        self._scenario_repo = scenario_repo
        self._enabled = enabled
        self._evaluator = None

    def start(self):
        super(EvaluatorWorker, self).start()
        actions_callback = VitrageNotifier(
            conf=self._conf,
            publisher_id='vitrage_evaluator',
            topic=EVALUATOR_TOPIC).notify
        self._entity_graph.notifier._subscriptions = []  # Quick n dirty
        self._evaluator = ScenarioEvaluator(
            self._conf,
            self._entity_graph,
            self._scenario_repo,
            actions_callback,
            self._enabled)
        self.tg.add_thread(self._read_queue)
        LOG.info("EvaluatorWorkerService - Started!")
        self._evaluator.scenario_repo.log_enabled_scenarios()

    def _read_queue(self):
        while True:
            next_task = self._task_queue.get()
            if next_task is POISON_PILL:
                self._task_queue.task_done()
                break
            try:
                self._do_task(next_task)
            except Exception as e:
                LOG.exception("Graph may not be in sync: exception %s", e)
            self._task_queue.task_done()
            # Evaluator queue may have been updated, thus the sleep:
            time.sleep(0)

    def _do_task(self, task):
            (before, current, is_vertex, action) = task
            if not action:
                self._graph_update(before, current, is_vertex)
            elif action == START_EVALUATION:
                self._evaluator.run_evaluator()

    def _graph_update(self, before, current, is_vertex):
        if current:
            if is_vertex:
                self._entity_graph.add_vertex(current)
            else:
                self._entity_graph.add_edge(current)
        else:
            if is_vertex:
                self._entity_graph.delete_vertex(before)
            else:
                self._entity_graph.delete_edge(before)

    def stop(self, graceful=False):
        super(EvaluatorWorker, self).stop(graceful)
        self.tg.stop()
        LOG.info("EvaluatorWorkerService - Stopped!")
