#! -*- coding: utf-8 -*-

"""
当 根目录 disk usage 达到 80% 时, 触发clean.sh 脚本, 先删除 4天前的log, 设定flag = 1
然后 如果 disk usage 还是 80%, 再次触发clean.sh 脚本, 删除 4 - flag 天前的log 一直循环
没达到disk usage 80% 不触发

"""

import psutil
import subprocess
import logging
import sys
import math

log = logging.getLogger()
log.setLevel(logging.NOTSET)
fh=logging.FileHandler('cron.log')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
log.addHandler(fh)


class CronDelete(object):
    def __init__(self, maxdate=4):
        self.maxdate = maxdate
        self.flag = 0


    def _check_flag(self):
        return  0 <= self.flag < self.maxdate

    def increase(self):
        self.flag += 1

    def _call_bash(self):

        script = '/bin/custom.sh'
        bash = '/bin/bash'
        args = str(self.maxdate - self.flag)
        cmd_list = [bash, script, args]
        p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.wait() == 0:
            for data in p.stdout.readlines():
                log.debug(data.decode('utf-8'))
        else:
            for data in p.stderr.readlines():
                log.critical(data.decode('utf-8'))

    def disk_usage(self):
        res = psutil.disk_usage('/')
        return math.ceil(res.percent)

    def check_usage(self):
        return self.disk_usage() > 80

    def do(self):
        if self._check_flag():
            self._call_bash()
        else:
            log.debug('the flag is over the max')
            sys.exit(-1)

if __name__ == "__main__":
    cron = CronDelete()
    while cron.check_usage():
        cron.do()
        cron.increase()
