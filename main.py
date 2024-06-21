#!/usr/bin/env python3
import os


import api_helper


def os_system(cmd):
    res = os.system(cmd)
    return f'Executed `{cmd}`\nresult={res}'


class ApiServer(api_helper.ApiHandler):
    def API_beep(self):
        return os_system('beep -f 700 -l 100')

    def API_suspend(self):
        os_system('bash -c "beep -f 1800 &"')
        return os_system('systemctl suspend')


def main():
    api_helper.start(ApiServer, 8090)


if __name__ == '__main__':
    main()
