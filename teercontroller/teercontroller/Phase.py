import Series
import Device
import time
import threading
import asyncio


class Phase:
    def __init__(self, duration, delay_between_series, evom, series, kill_flag, not_running_flag, lock, queue):
        """Initializes the fields taken from the request, and converts all of them to seconds."""
        assert isinstance(duration, (int, float)), duration
        assert isinstance(delay_between_series, (int, float)), delay_between_series
        assert isinstance(evom, Device.Device), evom
        assert isinstance(series, Series.Series), series
        # Usage of managers makes it difficult to make assertions:
        # assert isinstance(kill_flag, multiprocessing.Event), kill_flag
        # assert isinstance(not_running_flag, multiprocessing.Event), not_running_flag
        # assert isinstance(lock, multiprocessing.Lock), lock
        # assert isinstance(queue, multiprocessing.Queue), queue

        self.duration = duration
        self.delay_between_series = delay_between_series
        self.evom = evom
        self.series = series

        self.start_time = None
        self.end_time = None

        self.kill_flag = kill_flag
        self.not_running_flag = not_running_flag  # used because wait() triggers only on set(), not on clear()

        self.not_running_flag.set()
        self.lock = lock
        self.queue = queue


    def __str__(self):
        """Formatting for the class, only testing purposes.

        Returns:
            Human readable formatted string
        """
        return ("duration = " + str(self.duration) + "\n" +
                "delay = " + str(self.delay_between_series))

    def run(self, start_time):
        self.not_running_flag.clear()
        self.kill_flag.clear()

        self.start_time = next_series = time.time()
        self.end_time = time.time() + self.duration
        while time.time() <= self.end_time:
            if self.kill_flag.is_set():  # Exit condition, set everything to default then return
                self.lock.acquire()
                self.evom.low()
                self.queue.put("force stop")
                self.lock.release()
                return

            if time.time() >= next_series:
                self.lock.acquire()
                next_series = time.time() + self.delay_between_series

                if not self.evom.is_on:
                    self.evom.on()

                data = self.series.run()
                t = time.time() - start_time
                self.queue.put((t, data))

                if self.delay_between_series != 0:
                    self.evom.off()
                self.lock.release()

            time.sleep(0.1)
        self.lock.acquire()
        self.evom.off()
        self.not_running_flag.set()
        self.queue.put("natural stop")
        self.lock.release()
