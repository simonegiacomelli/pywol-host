#!/usr/bin/env python3
import os


import api_helper


def os_system(cmd):
    res = os.system(cmd)
    return f'Executed `{cmd}`\nresult={res}'


class ApiServer(api_helper.ApiHandler):
    def API_beep(self):
        return os_system('beep')

    def API_suspend(self):
        return os_system('systemctl suspend')


def main():
    api_helper.start(ApiServer, 8090)


if __name__ == '__main__':
    main()
