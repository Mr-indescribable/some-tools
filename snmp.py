#!/usr/bin/python3.6
#coding: utf-8

from enum import Enum

from pysnmp import hlapi


class SnmpVersions:

    V2C = 'v2c'
    V3 = 'v3'


class SnmpV3AuthProtos(Enum):

    NO_AUTH = hlapi.usmNoAuthProtocol
    HMAC_MD5 = hlapi.usmHMACMD5AuthProtocol
    HMAC_SHA = hlapi.usmHMACSHAAuthProtocol
    HMAC128_SHA224 = hlapi.usmHMAC128SHA224AuthProtocol
    HMAC192_SHA256 = hlapi.usmHMAC192SHA256AuthProtocol
    HMAC256_SHA384 = hlapi.usmHMAC256SHA384AuthProtocol
    HMAC384_SHA512 = hlapi.usmHMAC384SHA512AuthProtocol


class SnmpV3CryptoProtos(Enum):

    NO_ENCRYPTION = hlapi.usmNoPrivProtocol
    DES = hlapi.usmDESPrivProtocol
    DES_EDE = hlapi.usm3DESEDEPrivProtocol
    AES_128_CFB = hlapi.usmAesCfb128Protocol
    AES_192_CFB = hlapi.usmAesCfb192Protocol
    AES_256_CFB = hlapi.usmAesCfb256Protocol


class SnmpClient():

    ''' SNMP Client

    Supported SNMP v2c and v3.
    Users can provide the "community" argument to use SNMP v2c,
    otherwise, it's v3.
    '''

    def __init__(
        self, host, port=161, community=None,
        v3_user=None, v3_auth_proto=None, v3_auth_key=None,
        v3_crypto_proto=None, v3_crypto_key=None
    ):
        ''' Constructor

        :param host: target host, domain name or IP address, str
        :param port: target port, int
        :param community: SNMP v2c community, str
        :param v3_user: SNMP v3 username, str
        :param v3_auth_proto: SNMP v3 authorization protocol,
                              should be choosed from SnmpV3AuthProtos
        :param v3_auth_key: SNMP v3 authorization key, str
        :param v3_crypto_proto: SNMP v3 cryptography protocol,
                                should be choosed from SnmpV3CryptoProtos
        :param v3_crypto_key: SNMP v3 cryptography key, str
        '''

        self.target = (host, port)
        self.community = community
        self.v3_user = v3_user
        self.v3_auth_proto = v3_auth_proto
        self.v3_auth_key = v3_auth_key
        self.v3_crypto_proto = v3_crypto_proto
        self.v3_crypto_key = v3_crypto_key

        if community is not None:
            self.version = SnmpVersions.V2C
            self.auth_data = hlapi.CommunityData(self.community)
        else:
            self.version = SnmpVersions.V3

            if (
                self.v3_user is None or
                self.v3_auth_proto is None or
                self.v3_crypto_proto is None
            ):
                raise TypeError('Necessary arguments not provided')

            if self.v3_auth_proto not in SnmpV3AuthProtos:
                raise TypeError('Invalid SNMP v3 authorization protocol')

            if self.v3_crypto_proto not in SnmpV3CryptoProtos:
                raise DevError('Invalid SNMP v3 cryptography protocol')

            self.auth_data = hlapi.UsmUserData(
                                 self.v3_user,
                                 self.v3_auth_key,
                                 self.v3_crypto_key,
                                 self.v3_auth_proto,
                                 self.v3_crypto_proto,
                             )

    def get_by_var(self, mib_name, var_name, position=None):
        oid = (
            (mib_name, var_name) if position is None else
            (mib_name, var_name, position)
        )

        res = hlapi.getCmd(
                  hlapi.SnmpEngine(),
                  self.auth_data,
                  hlapi.UdpTransportTarget(self.target),
                  hlapi.ContextData(),
                  hlapi.ObjectType(
                      hlapi.ObjectIdentity(*oid)
                  ),
              )
        res = next(res)
        err_indication, err_status, err_index, var_binds = res
        return var_binds[0]

    def get_by_oid(self, oid):
        res = hlapi.getCmd(
                  hlapi.SnmpEngine(),
                  self.auth_data,
                  hlapi.UdpTransportTarget(self.target),
                  hlapi.ContextData(),
                  hlapi.ObjectType(
                      hlapi.ObjectIdentity(oid)
                  ),
              )
        res = next(res)
        err_indication, err_status, err_index, var_binds = res
        return var_binds[0]
