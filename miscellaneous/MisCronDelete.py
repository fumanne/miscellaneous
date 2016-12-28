#! -*- coding: utf-8 -*-

"""
当 根目录 disk usage 达到 80% 时, 触发clean.sh 脚本, 先删除 4天前的log, 设定flag = 1
然后 如果 disk usage 还是 80%, 再次触发clean.sh 脚本, 删除 4 - flag 天前的log 一直循环
没达到disk usage 80% 不触发

"""

import psutil
import subprocess

class CronDelete(object):
    def __init__(self, maxdate=4):
        self.maxdate = maxdate
        self._ST = maxdate
        self.flag = 0


    def _check_flag(self):
        return  0 <= self.flag < self._ST

    def reset(self):
        self.flag += 1

    def _call_bash(self):

        script = '/Users/kc-fu/shell/abc.sh'
        bash = '/bin/bash'
        args = str(self.maxdate - self.flag)
        cmd_list = [bash, script, args]
        p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(args)
        if p.wait() == 0:
            return p.returncode, p.stdout
        else:
            return p.returncode, p.stderr

    def disk_usage(self):
        res = psutil.disk_usage('/')
        return int(res.percent)

    def check_usage(self):
        return self.disk_usage() > 80

    def do(self):
        if self._check_flag():
            self._call_bash()
        else:
            raise ValueError

if __name__ == "__main__":
    cron = CronDelete()
    while cron.check_usage():
        cron.do()
        cron.reset()
        print(cron.flag)
