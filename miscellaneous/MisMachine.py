#! -*- coding: utf-8 -*-

import os
import socket
import fcntl
import struct
from .MisExceptions import SocketGetError


class BaseMachine(object):
    def __init__(self, name):
        self.name = name

    @property
    def cpu(self):
        return CPU()

    @property
    def mem(self):
        return MEM()

    @property
    def process(self, pid):
        return Process(pid)

    @property
    def net(self):
        return NET()


class CPU(object):
    File = '/proc/cpuinfo'

    def __init__(self):
        if not self.validate():
            raise IOError
        with open(CPU.File, 'r') as f:
            self.rawinfo = [i for i in f.read().split('\n\n') if i]

    def validate(self):
        return os.path.isfile(CPU.File)

    def infos(self):
        """
        :return: list of object Processor
        """
        return map(Processor, self.rawinfo)

    def gatherinfo(self):
        result = dict()
        physical = set([obj.physical_id for obj in self.infos()])
        model_name = set([obj.model_name for obj in self.infos()])
        vendor = set([obj.vendor for obj in self.infos()])
        cores = set([obj.cpu_cores for obj in self.infos()])
        mhz = set([obj.mhz for obj in self.infos()])
        result['Number of Pyhsical CPU'] = len(physical)
        result['Model_Name'] = model_name
        result['Vendor'] = vendor
        result['Number of cores per Pyhsical CPU'] = cores
        result['Mhz'] = mhz
        return result


class Processor(object):
    def __init__(self, long_str):
        self.long_str = long_str
        self.info = self.s2d(self.long_str)
        self.pid = int(self.info['processor'])

    def __repr__(self):
        return '<Processor-{} object>'.format(self.pid)

    __str__ = __repr__

    @staticmethod
    def s2d(line):
        _result = dict()
        for item in line.split('\n'):
            _tmp = item.replace('\t', '').split(":", 1)
            _result[_tmp[0]] = _tmp[1]
        return _result


    @property
    def processor_num(self):
        return self.pid

    @property
    def model_name(self):
        return self.info['model name']

    @property
    def physical_id(self):
        return self.info['physical id']

    @property
    def vendor(self):
        return self.info['vendor_id']

    @property
    def core_id(self):
        return self.info['core id']

    @property
    def mhz(self):
        return self.info['cpu MHz']

    @property
    def cpu_cores(self):
        return self.info['cpu cores']

    @property
    def flags(self):
        return self.info['flags']


class MEM(object):
    File = '/proc/meminfo'

    def __init__(self):
        with open(MEM.File, 'r') as f:
            _info = f.readlines()
        self.meminfo = dict([i.strip().replace('\t', '').split(":") for i in _info if ':' in i])

    @property
    def mem_total(self):
        return self.meminfo['MemTotal']

    @property
    def mem_free(self):
        return self.meminfo['MemFree']

    @property
    def buffers(self):
        return self.meminfo['Buffers']

    @property
    def cached(self):
        return self.meminfo['Cached']

    @staticmethod
    def myfilter(x):
        if x[0] == 'MemTotal' or x[0] == 'MemFree' or x[0] == 'Buffers' or x[0] == 'Cached':
            return x
        else:
            return False

    @property
    def simple_meminfo(self):
        return dict(filter(self.myfilter, self.meminfo.items()))


class Process(object):
    ROOT = '/proc'
    STATUS = 'status'

    def __init__(self, pid):
        self.pid = pid
        self.abspath = os.path.join(Process.ROOT, self.pid, Process.STATUS)

    def validate(self):
        if os.path.isfile(self.abspath):
            return True
        else:
            return False

    @staticmethod
    def myfilter(x):
        if x[0] == "Name" or x[0] == "PPid" or x[0] == 'Threads' or x[0] == 'Pid' or x[0] == 'State' or x[0] == 'PPid':
            return x
        else:
            return False

    @property
    def status(self):
        if not self.validate():
            raise FileNotFoundError('the {} is not Found'.format(self.pid))
        with open(self.abspath) as f:
            content = f.readlines()
        return dict([i.strip().replace('\t', '').split(":", 1) for i in content if ":" in i])

    @property
    def simple_status(self):
        return dict(filter(self.myfilter, self.status.items()))


class NET(object):
    File = '/proc/net/if_inet6'
    IPSIZE = '256s'
    IPPOSIX = 15
    IPPOSITION = 0x8915

    def localip(self, interface):
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            pkgstring = fcntl.ioctl(skt.fileno(), NET.IPPOSITION, struct.pack(NET.IPSIZE, interface[:NET.IPPOSIX]))
        except IOError:
            raise IOError("Error!, No {} interface".format(interface))
        else:
            ipstring = socket.inet_ntoa(pkgstring[20:24])
            return ipstring

    def listinterface(self):
        with open(NET.File) as f:
            content = f.readlines()
        return [i.strip().split()[-1] for i in content]

    def listip(self):
        result = []
        for interface in self.listinterface():
            result.append(self.localip(interface))
        return result

    @property
    def localhostname(self):
        return socket.gethostname()

    def remotehostname(self, remote_name, extra=False):
        if not extra:
            try:
                result = socket.gethostbyname(remote_name)
            except:
                raise SocketGetError('invalidate domain {}'.format(remote_name))
        else:
            try:
                result = socket.gethostbyname_ex(remote_name)
            except:
                raise SocketGetError('invalidate domain {}'.format(remote_name))
        return result

    # TODO: add more
