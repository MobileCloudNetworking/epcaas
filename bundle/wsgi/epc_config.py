# Copyright (c) 2014, Telecom Italia SpA

"""
Service Orchestrator for OpenEPC.
MCN 2014
"""

__author__ = '00917777'

# import os
import logging
# import paramiko
# import DNSaaSClient
from utils import *
from globals import *

import nat
import mme
import pgwu_sgwu


def config_logger(log_level=logging.DEBUG):
    """
    Creates a logger with a default syntax of the output string
    :param log_level: DEBUG by default

    :return: the logger

    """
    logging.basicConfig(
        format='%(threadName)s \t %(levelname)s %(asctime)s: \t%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        log_level=log_level)
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    return logger


LOG = config_logger()


def pre_stop_switch(conf_param, output):

    # remove sw dependency from nat
    c = nat.NatAdapter(conf_param['conf_proxy'])
    nat_ip = get_ips(output, 'mcn.endpoint.nat')
    nat_ip_net_a = get_ips(output, 'nat.net_a.ip')

    config = {
        'GW_NET_A_IP': nat_ip_net_a,
        'GW_NET_MGMT_IP': nat_ip
        }
    config['floating_ips'] = {'mgmt': nat_ip}

    c.remove_dependency(config)

    # remove sw dependency from mme
    c = mme.MMEAdapter(conf_param['conf_proxy'])
    mme_ip = get_ips(output, 'mcn.endpoint.mme-pgwc-sgwc')

    config = {
        'PGW_U_DATAPATH_ID': '3812090105000000'
    }
    config['floating_ips'] = {'mgmt': mme_ip}

    c.remove_dependency(config)

    # remove nat dependency on sw
    c = pgwu_sgwu.PgwuSgwuAdapter(conf_param['conf_proxy'])
    pgwu1_ip = get_ips(output, 'mcn.endpoint.pgwu-sgwu-1')
    pgwu1_ip_net_a = get_ips(output, 'pgwu-sgwu-1.net_a.ip')

    config = {
        'PGWU_SGWU_NET_A_IP': pgwu1_ip_net_a
    }
    config['floating_ips'] = {'mgmt': pgwu1_ip}

    c.remove_dependency(config)

    return 0


def config_nat(parameters, conf_param, output):

    c = nat.NatAdapter(conf_param['conf_proxy'])

    zabbix_ip = parameters['maas_ip_address']

    # Processing heat output string to get endpoints and parameters
    nat_ip = get_ips(output, 'mcn.endpoint.nat')
    nat_ip_net_a = get_ips(output, 'nat.net_a.ip')
    pgwu1_ip = get_ips(output, 'mcn.endpoint.pgwu-sgwu-1')
    pgwu1_ip_net_a = get_ips(output, 'pgwu-sgwu-1.net_a.ip')

    config = {
        'hostname': NAT_VM_NAME,
        'ips': {'mgmt': nat_ip, 'net_a': nat_ip_net_a},
        'zabbix_ip': zabbix_ip,
        'floating_ips': {'mgmt': nat_ip}
    }
    c.preinit(config)

    config = {
        'floating_ips': {'mgmt': nat_ip}
    }
    c.install(config)

    config = {
        'CLOUD_MGMT_GW_IP': conf_param['gw_mgmt'],
        'GW_NET_A_IP': nat_ip_net_a,
        'GW_NET_A_IP_ENDING_NUMBER': nat_ip_net_a.split('.')[3],
        'GW_NET_MGMT_IP': nat_ip,
        'PGWU_NET_A_IP_ENDING_NUMBER': pgwu1_ip.split('.')[3],
        'PGW_U_NET_A_IP': pgwu1_ip_net_a,
        'STATIC_NUMBER': '1',
        'ZABBIX_IP': zabbix_ip
    }

    config['VIRT_NET_A_GW_IP'] = '192.168.77.' + config['GW_NET_A_IP_ENDING_NUMBER']
    config['VIRT_NET_A_INTF'] = 'gwtun' + config['PGWU_NET_A_IP_ENDING_NUMBER']
    config['VIRT_NET_A_PGWU_IP'] = '192.168.77.' + config['PGWU_NET_A_IP_ENDING_NUMBER']
    config['floating_ips'] = {'mgmt': nat_ip}
    c.add_relation(config)

    config = {}
    config['floating_ips'] = {'mgmt': nat_ip}
    c.start(config)

    return 0


def config_mme_sgwc_pgwc(parameters, conf_param, output):

    c = mme.MMEAdapter(conf_param['conf_proxy'])

    zabbix_ip = parameters['maas_ip_address']
    dns_ip = parameters['dnsaas_ip_address']

    nat_ip = get_ips(output, 'mcn.endpoint.nat')
    nat_ip_net_a = get_ips(output, 'nat.net_a.ip')
    pgwu1_ip = get_ips(output, 'mcn.endpoint.pgwu-sgwu-1')
    pgwu1_ip_net_a = get_ips(output, 'pgwu-sgwu-1.net_a.ip')
    mme_ip = get_ips(output, 'mcn.endpoint.mme-pgwc-sgwc')
    mme_ip_net_d = get_ips(output, 'mme-pgwc-sgwc.net_d.ip')
    pgwu1_ip_net_d = get_ips(output, 'pgwu-sgwu-1.net_d.ip')
    pgwu_sgwu_public_ip = get_ip(output, 'pgwu-sgwu-1_public_ip')
    
    # preinit
    config = {}
    config['hostname'] = MME_VM_NAME
    config['ips'] = {'mgmt': mme_ip, 'net_d': mme_ip_net_d}
    config['zabbix_ip'] = zabbix_ip
    config['floating_ips'] = {'mgmt': mme_ip}
    c.preinit(config)

    # install
    config = {}
    config = {
        'MME_MGMT_IP': mme_ip,
        'MME_CONSOLE_PORT': '10080',
        'MME_NET_D_IP': mme_ip_net_d,
        'OFP_PORT': '6634',
        'OFP_PROTOCOL': 'tcp',
        'NETD_FLOATING_NETWORK_CIDR': '193.55.112.80'
    }
    config['floating_ips'] = {'mgmt': mme_ip}
    c.install(config)

    # # add dependency to enodeb
    # config = {}
    # config = {
    # 'ENODEB_NAME': 'enodeb',
    # 'NETWORK_IP':'192.168.3.0',
    # 'NETWORK_MASK':'255.255.255.0',
    # 'NETWORK_START':'192.168.3.100',
    # 'NETWORK_END': '192.168.3.130'
    # }
    # config['floating_ips'] = {'mgmt':'160.85.4.49'}
    # c.add_dependency(config, 'enodeb')
    #
    # # add dependency to bt
    # config = {}
    # config = {
    # 'BT_NAME':'BT-5G-2675998530',
    # 'NETWORK_IP':'192.168.4.0',
    # 'NETWORK_MASK':'255.255.255.0',
    # 'NETWORK_START':'192.168.4.100',
    # 'NETWORK_END': '192.168.4.130'
    # }
    # config['floating_ips'] = {'mgmt':'160.85.4.49'}
    # c.add_dependency(config, 'bt')

    # add dependency to dns
    config = {}
    config = {
    'DNS_IP': dns_ip,
    'DNS_REALM':'epc.mnc001.mcc001.3gppnetwork.org',
    'DNS_LISTEN': mme_ip # mme mgmt ip
    }
    config['floating_ips'] = {'mgmt': mme_ip}
    c.add_dependency(config, 'dns')

    # add dependency to pgw_u
    config = {}
    config = {
    'OFP_DATAPATH_ID':'3812090105000000',
    'PGW_U_Upload_Interface_IP': pgwu_sgwu_public_ip,
    'PGW_U_Download_Interface_IP': pgwu1_ip_net_d
    }
    config['floating_ips'] = {'mgmt': mme_ip}
    c.add_dependency(config, 'pgw_u')

    # prestart
    config = {}
    config = {
 'MME_MGMT_IP': mme_ip,
 'SGW_IP': pgwu1_ip_net_d, #net_d ip of pgwu-sgwu
 'MME_CONSOLE_PORT': '10080',
 'MME_NET_D_IP': mme_ip_net_d,
 'DNS_REALM': 'epc.mnc001.mcc001.3gppnetwork.org',
 'SGWU_PGWU_FLOATING_IP_NET_D': pgwu_sgwu_public_ip,  # local IP of net_d
 'ENODEB_NET_C_IP': '6.6.6.40',   # not used
 'HSS_NAME':'slf',  #static
 'HSS_PORT':'13868',  #static
 'OFP_PORT':'6634',
 'OFP_PROTOCOL':'tcp',
 'SGWU_PGWU_NET_D': pgwu1_ip_net_d
    }
    config['floating_ips'] = {'mgmt': mme_ip}
    c.pre_start(config)

    # start
    config = {}
    config['floating_ips'] = {'mgmt': mme_ip}
    c.start(config)

    return 0


def config_pgwu_sgwu(parameters, conf_param, output):

    c = pgwu_sgwu.PgwuSgwuAdapter(conf_param['conf_proxy'])

    zabbix_ip = parameters['maas_ip_address']
    dns_ip = parameters['dnsaas_ip_address']

    nat_ip = get_ips(output, 'mcn.endpoint.nat')
    nat_ip_net_a = get_ips(output, 'nat.net_a.ip')
    pgwu1_ip = get_ips(output, 'mcn.endpoint.pgwu-sgwu-1')
    pgwu1_ip_net_a = get_ips(output, 'pgwu-sgwu-1.net_a.ip')
    mme_ip = get_ips(output, 'mcn.endpoint.mme-pgwc-sgwc')
    mme_ip_net_d = get_ips(output, 'mme-pgwc-sgwc.net_d.ip')
    pgwu1_ip_net_d = get_ips(output, 'pgwu-sgwu-1.net_d.ip')


    # preinit
    config = {}
    config['hostname'] = PGW1_VM_NAME
    config['ips'] = {'mgmt': pgwu1_ip, 'net_a': pgwu1_ip_net_a,
                      'net_d': pgwu1_ip_net_d}
    config['zabbix_ip'] = zabbix_ip
    config['floating_ips'] = {'mgmt': pgwu1_ip}
    c.preinit(config)

    # install
    config = {}
    config = {'OFP_DATAPATH_ID': '3812090105000000',
 'PGWU_SGWU_ID': '3812090105',
 'PGWU_SGWU_NET_MGMT_IP': pgwu1_ip,
 'PGW_U_Download_Interface_IP': pgwu1_ip_net_a,   #net_a
 'PGW_U_Upload_Interface_IP': pgwu1_ip_net_d,    # net_d
 'UPLOAD_FLOATING_NETWORK_CIDR': conf_param['cidr_float']}  #floating ip subnet cidr
    config['floating_ips'] = {'mgmt': pgwu1_ip}
    c.install(config)

    # add dependency to gw(nat)
    config = {}
    config = {
    'PGWU_SGWU_NET_A_IP': pgwu1_ip_net_a,
    'GW_NET_A_IP': nat_ip_net_a,
    # The last number from the net_a IP of the pgwu-sgwu
    'PGWU_NET_A_IP_ENDING_NUMBER': pgwu1_ip.split('.')[3],
    # The last number from the net_a IP of the gw
    'GW_NET_A_IP_ENDING_NUMBER': nat_ip_net_a.split('.')[3]
    }
    config['VIRT_NET_A_IP'] = '192.168.77.' + config['PGWU_NET_A_IP_ENDING_NUMBER'] # e.g. 192.168.77.210 when pgwu-sgwu got 172.30.5.210
    config['VIRT_NET_A_GW_IP'] = '192.168.77.' + config['GW_NET_A_IP_ENDING_NUMBER'] # e.g. 192.168.77.204 when gw got 172.20.5.204
    config['floating_ips'] = {'mgmt': pgwu1_ip}
    c.add_dependency(config, 'gw')

    # add dependency to pgw_c
    config = {}
    config = {
    'PGW_C_Openflow_Transport_Protocol':'tcp',
    'PGW_C_Openflow_IP': mme_ip, # The MGMT_IP of mme
    'PGW_C_OpenFlow_Port':'6634'
    }
    config['floating_ips'] = {'mgmt': pgwu1_ip}
    c.add_dependency(config, 'pgw_c')

    # prestart
    config = {}
    config = {
 'PGWU_SGWU_ID': '3812090105',
 'PGWU_SGWU_NET_MGMT_IP': pgwu1_ip,
 'PGW_U_Download_Interface_IP': pgwu1_ip_net_a,   #net_a
 'PGW_U_Upload_Interface_IP': pgwu1_ip_net_d,    # net_d
 'OFP_DATAPATH_ID': '3812090105000000',
 'PGW_C_Openflow_IP': mme_ip, # The MGMT_IP of mme
 'PGW_C_OpenFlow_Port':'6634'
    }
    config['floating_ips'] = {'mgmt': pgwu1_ip}
    c.pre_start(config)

    config = {}
    config['floating_ips'] = {'mgmt': pgwu1_ip}
    c.start(config)

    return 0


class EPCConfig(object):
    """
    Function to configure OpenEPC nodes after they have been deployed
    """

    def __init__(self):
        """
        docstring stub
        """
        pass

    def config(self, parameters, conf_param, output):
        """
        Performs the actual configuration of the running SIC
        """

        if parameters is None:
            return -1

        if config_nat(parameters, conf_param, output) < 0:
            LOG.debug('NAT config FAILED')
            return -1

        if config_mme_sgwc_pgwc(parameters, conf_param, output) < 0:
            LOG.debug('MME config FAILED')
            return -1

        if config_pgwu_sgwu(parameters, conf_param, output) < 0:
            LOG.debug('PGWC-SGWC config FAILED')
            return -1

        return 0

    def config_dnsaas(self, dnsaas, output, token):
        """
        Configures DNSaaS with the correct records needed by OpenEPC. This
        method only configures an A record needed by MME.
        If domain is not available, create it

        :param dnsaas: the DNSaaS object, created on first update
        :param output: the output string from heat
        :param token: keystone auth token, owned by EPC SO Execution

        :return: 0 if ok, -1 otherwise
        """

        mme_ip = get_ips(output, 'mcn.endpoint.mme-pgwc-sgwc')
        print mme_ip

        domain_name = 'epc.mnc001.mcc001.3gppnetwork.org'
        email_name = 'admin@mobile-cloud-networking.eu'
        ttl = 3600
        rec_name = 'mme'
        rec_type = 'A'

        status = dnsaas.get_domain(domain_name, token)
        print status

        if status['code'] >= 400:  # domain not configured
            LOG.debug('DNSaaS config: domain not configured')
            if dnsaas.create_domain(domain_name, email_name, ttl, token) < 1:
                LOG.debug('DNSaaS config: create_domain failed')
                return -1

            if dnsaas.create_record(domain_name, rec_name,
                                    rec_type, mme_ip, token) < 1:
                LOG.debug('DNSaaS config: create_record failed')
                return -1
            LOG.debug('DNSaaS config: create_domain and create_record OK')
        else:
            status = dnsaas.get_record(domain_name, rec_name, rec_type, token)

            # record not configured
            if 'code' in status and status['code'] >= 400:
                LOG.debug('DNSaaS config: domain ok, but record not configured')
                if dnsaas.create_record(domain_name, rec_name,
                                        rec_type, mme_ip, token):
                    LOG.debug('DNSaaS config: create_record failed')
                    return -1
        LOG.debug('DNSaaS config: OK')

    # def config_dnsaas(self, dnsaas_ip_address, token):

    #     DNSaaSClient.DNSaaSClientCore.apiurlDNSaaS = \
    #         'http://' + dnsaas_ip_address + ':8080'
    #
    #     if DNSaaSClient.getDomain('epc.mnc001.mcc001.3gppnetwork.org',
    #                               token) != 0:
    #
    #         # If domain exists, configure 'A' record for MME in the DNSaaS (
    #         # if it is not there yet)
    #         if DNSaaSClient.getRecord(
    #                 domain_name='epc.mnc001.mcc001.3gppnetwork.org',
    #                 record_name='mme',
    #                 record_type='A',
    #                 tokenId=token) == 0:
    #             # record not exists, create it
    #             res_cr = DNSaaSClient.createRecord(
    #                 domain_name='epc.mnc001.mcc001.3gppnetwork.org',
    #                 record_name='mme',
    #                 record_type='A',
    #                 record_data='192.168.9.47',
    #                 tokenId=token)
    #             if res_cr != 0:
    #                 LOG.debug(
    #                     'Record correctly created on DNSaaS ' +
    #                     dnsaas_ip_address + ' with return code: ' +
    #                     str(res_cr))
    #                 return 0
    #             else:
    #                 LOG.debug(
    #                     'Failed record creation on DNSaaS ' +
    #                     dnsaas_ip_address + ' with return code: ' +
    #                     str(res_cr))
    #                 return -1
    #         else:
    #             LOG.debug(
    #                 'Record already configured on DNSaaS ' + dnsaas_ip_address)
    #             return 0
    #     else:
    #         LOG.debug('DOMAIN not configured on DNSaaS ' + dnsaas_ip_address)
    #         return -1
        return 0

    def shutdown_pgw(self, conf_param, output):
        """
        Gracefully shuts down PGW.
        :return: 0 on success, -1 otherwise

        """

        return pre_stop_switch(conf_param, output)
        # client = paramiko.SSHClient()
        #
        # pkey_file = os.path.join(SO_DIR, 'data', MCN_PRIVATE_KEY_FILE)
        # if os.path.isfile(pkey_file):
        #     LOG.debug('Key filename: ' + pkey_file)
        # else:
        #     LOG.debug('Key filename NOT FOUND')
        #     return -1
        #
        # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #
        # try:
        #     client.connect(pgw_ipaddress, username='ubuntu',
        #                    key_filename=pkey_file)
        #     LOG.debug('*** ssh CONNECTED ***')
        # except BaseException as exc:
        #     print '*** Caught exception: %s: %s' % (exc.__class__, exc)
        #     LOG.debug('*** ssh CONNECTION FAILED***')
        #     return -1
        #
        # command = 'sudo stop sgwu-pgwu'
        # try:
        #     stdin, stdout, stderr = client.exec_command(command)
        # except BaseException as exc:
        #     print '*** Caught exception: %s: %s' % (exc.__class__, exc)
        #     LOG.debug('*** ssh exec_command send FAILED ***')
        #     return -1
        #
        # print stdout.readlines()
        # return 0
