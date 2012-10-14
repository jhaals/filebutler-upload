from datetime import datetime, timedelta
import sys


class ProgressBar(object):
    def __init__(self, filename, fmt):
        self.filename = filename
        self.fmt = fmt
        self.progress = 0
        self.total = 0
        self.time_started = datetime.now()
        self.time_updated = self.time_started

    def __call__(self, current, total):
        self.progress = current
        self.total = total

        if datetime.now() - self.time_updated > timedelta(seconds=0.5):
            output = self.fmt.format(
                filename=self.filename,
                percent=self.get_percent(),
                speed=self.get_mbps()
            )

            sys.stdout.write('\r' + output)
            sys.stdout.flush()
            self.time_updated = datetime.now()

    def get_percent(self):
        return self.progress / float(self.total)

    def get_mbps(self):
        time_delta = datetime.now() - self.time_started

        if not time_delta.seconds:
            return 0

        return self.progress * 8 / float(time_delta.seconds) / 1000 / 1000
