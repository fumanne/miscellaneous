#! -*- coding: utf-8 -*-
#
# encapsulate the most useful service like Regions, EC2, VPC, RDS, IAM, S3, ElastiCache  in Chinese AWS.
# List all attribute from different service as mentioned.
#


from boto.regioninfo import RegionInfo, get_regions
from abc import ABCMeta, abstractmethod
from boto.ec2 import EC2Connection
from boto.vpc import VPCConnection
from boto.s3.connection import S3Connection
from boto.rds import RDSConnection
from boto.iam import IAMConnection
from boto.elasticache.layer1 import ElastiCacheConnection


class SimplyAWSAbstract(metaclass=ABCMeta):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region=None, **kwargs):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region = region
        self.kwargs = kwargs

    def __repr__(self):
        return self.__class__.__name__

    __str__ = __repr__

    @property
    def _isRegionInfo(self):
        return 'region' in self.kwargs and isinstance(self.kwargs['region'], RegionInfo) \
               and self.kwargs['region'].name == self.region

    @abstractmethod
    def _connect_to_region(self, **kwargs):
        raise NotImplementedError


    def all_region(self, name='ec2'):
        return get_regions(name)


class EC2(SimplyAWSAbstract):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region=None,  **kwargs):
        super(EC2, self).__init__(aws_access_key_id, aws_secret_access_key, region, **kwargs)
        self.name = self.__class__.__name__.lower()
        self.con = self._connect_to_region(**kwargs)

    def _connect_to_region(self, **kwargs):
        if not self._isRegionInfo:
            return EC2Connection(aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key,
                                 **kwargs)

        for region in self.all_region(self.name):
            if region.name == self.region:
                self.region = region

        return EC2Connection(aws_access_key_id=self.aws_access_key_id,
                             aws_secret_access_key=self.aws_secret_access_key,
                             region=self.region, **kwargs)


class VPC(SimplyAWSAbstract):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region=None, **kwargs):
        super(VPC, self).__init__(aws_access_key_id, aws_secret_access_key, region, **kwargs)
        self.con = self._connect_to_region(**kwargs)

    def _connect_to_region(self, **kwargs):
        if self._isRegionInfo:
            return VPCConnection(aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key,
                                 **kwargs)
        for region in self.all_region():
            if region.name == self.region:
                self.region = region

        return VPCConnection(aws_access_key_id=self.aws_access_key_id,
                             aws_secret_access_key=self.aws_secret_access_key,
                             region=self.region, **kwargs)


class S3(SimplyAWSAbstract):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, **kwargs):
        super(S3, self).__init__(aws_access_key_id, aws_secret_access_key, **kwargs)
        self.name = self.__class__.__name__.lower()
        self.con = self._connect_to_region(**kwargs)

    def _connect_to_region(self, **kwargs):
        return S3Connection(aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key, **kwargs)


class RDS(SimplyAWSAbstract):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region=None, **kwargs):
        super(RDS, self).__init__(aws_access_key_id, aws_secret_access_key, region, **kwargs)
        self.name = self.__class__.__name__.lower()
        self.con = self._connect_to_region(**kwargs)

    def _connect_to_region(self, **kwargs):
        if self._isRegionInfo:
            return RDSConnection(aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key,
                                 **kwargs)
        for region in self.all_region(self.name):
            if region.name == self.region:
                self.region = region

        return RDSConnection(aws_access_key_id=self.aws_access_key_id,
                             aws_secret_access_key=self.aws_secret_access_key,
                             region=self.region, **kwargs)


class ElastiCache(SimplyAWSAbstract):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region=None, **kwargs):
        super(ElastiCache, self).__init__(aws_access_key_id, aws_secret_access_key, region, **kwargs)
        self.name = self.__class__.__name__.lower()
        self.con = self._connect_to_region(**kwargs)

    def _connect_to_region(self, **kwargs):
        if self._isRegionInfo:
            return ElastiCacheConnection(aws_access_key_id=self.aws_access_key_id,
                                         aws_secret_access_key=self.aws_secret_access_key, **kwargs)
        for region in get_regions(self.name):
            if region.name == self.region:
                self.region = region

        return ElastiCacheConnection(aws_access_key_id=self.aws_access_key_id,
                                     aws_secret_access_key=self.aws_secret_access_key,
                                     region=self.region, **kwargs)


class IAM(SimplyAWSAbstract):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, **kwargs):
        super(IAM, self).__init__(self, aws_access_key_id, aws_secret_access_key, **kwargs)
        self.name = self.__class__.__name__.lower()
        self.con = self._connect_to_region(**kwargs)

    def _connect_to_region(self, **kwargs):
        return IAMConnection(aws_access_key_id=self.aws_access_key_id,
                             aws_secret_access_key=self.aws_secret_access_key, **kwargs)
