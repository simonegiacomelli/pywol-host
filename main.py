#!/usr/bin/env python3
import getpass
import os
import subprocess
import time
import urllib.request

from api_helper import ApiHandler


def os_system(cmd):
    res = os.system(cmd)
    return f'Executed `{cmd}`\nresult={res}'


class ApiServer(ApiHandler):

    def API_pollon_wake(self):
        return os_system('wake pollon0; wake pollon1')

    def API_pollon_sleep(self):
        return os_system("ssh pollon -t 'bash -i -c pm-suspend'")

    def API_pollon_ping(self):
        cmd = "timeout 0.1 ping 10.2.2.76 -c 1"
        res = os.system(cmd)
        status = 'pollon ok' if res == 0 else 'pollon is NOT PINGING'
        return f'Executed `{cmd}`\nresult={res}\nstatus={status}'

    def API_auto_run(self):
        return self.API_pollon_ping()


def main():
    import api_helper
    api_helper.start(ApiServer, 8090)


if __name__ == '__main__':
    main()
