"""
    :codeauthor: Pedro Algarvio (pedro@algarvio.me)


    tests.integration.modules.event
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import queue
import threading
import time

import pytest
import salt.utils.event as event
from tests.support.case import ModuleCase


@pytest.mark.windows_whitelisted
@pytest.mark.usefixtures("salt_sub_minion")
class EventModuleTest(ModuleCase):
    def __test_event_fire_master(self):
        events = queue.Queue()

        def get_event(events):
            with event.MasterEvent(self.master_opts["sock_dir"], listen=True) as me:
                events.put_nowait(me.get_event(wait=10, tag="salttest", full=False))

        threading.Thread(target=get_event, args=(events,)).start()
        time.sleep(1)  # Allow multiprocessing.Process to start

        ret = self.run_function(
            "event.fire_master", ["event.fire_master: just test it!!!!", "salttest"]
        )
        self.assertTrue(ret)

        eventfired = events.get(block=True, timeout=10)
        self.assertIsNotNone(eventfired)
        self.assertIn("event.fire_master: just test it!!!!", eventfired["data"])

        ret = self.run_function(
            "event.fire_master",
            ["event.fire_master: just test it!!!!", "salttest-miss"],
        )
        self.assertTrue(ret)

        with self.assertRaises(queue.Empty):
            eventfired = events.get(block=True, timeout=10)

    def __test_event_fire(self):
        events = queue.Queue()

        def get_event(events):
            with event.MinionEvent(self.minion_opts, listen=True) as me:
                events.put_nowait(me.get_event(wait=10, tag="salttest", full=False))

        threading.Thread(target=get_event, args=(events,)).start()
        time.sleep(1)  # Allow multiprocessing.Process to start

        ret = self.run_function(
            "event.fire", ["event.fire: just test it!!!!", "salttest"]
        )
        self.assertTrue(ret)

        eventfired = events.get(block=True, timeout=10)
        self.assertIsNotNone(eventfired)
        self.assertIn("event.fire: just test it!!!!", eventfired)

        ret = self.run_function(
            "event.fire", ["event.fire: just test it!!!!", "salttest-miss"]
        )
        self.assertTrue(ret)

        with self.assertRaises(queue.Empty):
            eventfired = events.get(block=True, timeout=10)

    def __test_event_fire_ipc_mode_tcp(self):
        events = queue.Queue()

        def get_event(events):
            with event.MinionEvent(self.sub_minion_opts, listen=True) as me:
                events.put_nowait(me.get_event(wait=10, tag="salttest", full=False))

        threading.Thread(target=get_event, args=(events,)).start()
        time.sleep(1)  # Allow multiprocessing.Process to start

        ret = self.run_function(
            "event.fire",
            ["event.fire: just test it!!!!", "salttest"],
            minion_tgt="sub_minion",
        )
        self.assertTrue(ret)

        eventfired = events.get(block=True, timeout=10)
        self.assertIsNotNone(eventfired)
        self.assertIn("event.fire: just test it!!!!", eventfired)

        ret = self.run_function(
            "event.fire",
            ["event.fire: just test it!!!!", "salttest-miss"],
            minion_tgt="sub_minion",
        )
        self.assertTrue(ret)

        with self.assertRaises(queue.Empty):
            eventfired = events.get(block=True, timeout=10)
