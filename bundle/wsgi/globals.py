# Copyright (c) 2014, Telecom Italia SpA

"""
Service Orchestrator for OpenEPC.
MCN 2014
"""

__author__ = 'sruffino'

CPU_LOAD = 0
ATTCH_USERS = 1
BW_OCC = 2
NUM_SWITCHES = 3

METRICS = {
    CPU_LOAD: 'CPU_IDLE',
    ATTCH_USERS: 'ATTCH_USERS',
    BW_OCC: 'BW_OCC',
    NUM_SWITCHES: 'NUM_SWITCHES'
}

TESTING_TILAB = False

MME_VM_NAME = 'mme-pgwc-sgwc'
PGW2_VM_NAME = 'pgwu-sgwu-2'
PGW2_ENDPOINT = 'mcn.endpoint.pgwu-sgwu-2'
PGW1_VM_NAME = 'pgwu-sgwu-1'
PGW1_ENDPOINT = 'mcn.endpoint.pgwu-sgwu-1'
NAT_VM_NAME = 'nat'
NAT_ENDPOINT = 'mcn.endpoint.nat'

USE_FIP_FOR_VMs = False

TSO_ATTCH_USERS = 100.0
TSI_ATTCH_USERS = 20.0
TSO_CPU_LOAD = 90.0
TSI_CPU_LOAD = 90.0

SCALING_GUARD_TIME = 300    # seconds after which a new scaling is allowed

MCN_PRIVATE_KEY_FILE = 'mcn-tub.pem'

DEFAULT_REGION = 'UBern'

# Ubern
ubern_parameters = {
    'public_net_id': 'fde9f17b-eb51-4d4b-a474-deb583d03d86',   # public
    'private_mgmt_net_id': '367d1aba-c539-46e1-8047-65c28283d9c9',  # mgmt
    'private_net_a_id': 'd291a440-fd7d-4025-b676-2ac8f132005b',  # neta
    'private_net_d_id': 'e780d5d6-78a9-46dc-8a3f-ed588379afa2',  # netd
    #private_net_c_id = 'b7cefba5-9035-4179-b146-69f9159a0c1c'  # netc
    'maas_ip_address': '130.92.70.184',  # default, static on ubern
    'maas_uid': 'admin',
    'maas_pwd': 'zabbix',
    'dnsaas_ip_address': '192.168.85.112',  # default, static on ubern
    'cidr_mgmt': '192.168.85.0/24',
    'cidr_float': '193.55.112.80',
    #'cidr_float': '130.92.70.128/25',
    'gw_mgmt': '192.168.85.1',
    'image': 'epc-base-r206',
    'mgmt_prefix': '192.168.85',
    'conf_proxy': '130.92.70.175'
                # default, static on ubern; it is a squid proxy
                # needed for configuring the epcaas vms
                # without requiring floating ip assigned to them
}

# these parameters are passed to heat during deploy, so they must be known
# in advance (i.e. they must not contain parameters which depend on other
# sic or support services)
ubern_heat_parameters = {
    'public_net_id': ubern_parameters['public_net_id'],
    'private_mgmt_net_id': ubern_parameters['private_mgmt_net_id'],
    'private_net_a_id': ubern_parameters['private_net_a_id'],
    'private_net_d_id': ubern_parameters['private_net_d_id'],
    'dnsaas_ip_address': ubern_parameters['dnsaas_ip_address'],
    'cidr_mgmt': ubern_parameters['cidr_mgmt'],
    'gw_mgmt': ubern_parameters['gw_mgmt'],
    'image': ubern_parameters['image'],
    'mgmt_prefix': ubern_parameters['mgmt_prefix']
}

# Bart (aka RegionOne)
bart_parameters = {
    'public_net_id': '831c6cfe-3f05-4fcc-9488-ca4e3106d748',   # public
    'private_mgmt_net_id': '14348f08-19c5-471d-9f8d-dfeff6ffdb1e',  # mgmt
    'private_net_a_id': 'd586a3bd-b04a-4132-80a6-9f4f9b379194',  # neta
    'private_net_d_id': '5b3daa20-142e-4e6d-9ed9-d22d2cdbaae7',  # netd
    #private_net_c_id = 'b7cefba5-9035-4179-b146-69f9159a0c1c'  # netc
    'maas_ip_address': '160.85.4.52',  # default, static
    'maas_uid': 'admin',
    'maas_pwd': 'zabbix',
    'dnsaas_ip_address': '192.168.9.143',  # default, static
    'cidr_mgmt': '192.168.9.0/24',
    'cidr_float': '160.85.4.0/24',
    'gw_mgmt': '192.168.9.1',
    'image': 'epc-base',
    'mgmt_prefix': '192.168.9',
    'conf_proxy': '160.85.4.41'
                # default, static on ubern; it is a squid proxy
                # needed for configuring the epcaas vms
                # without requiring floating ip assigned to them
}

# these parameters are passed to heat during deploy, so they must be known
# in advance (i.e. they must not contain parameters which depend on other
# sic or support services)
bart_heat_parameters = {
    'public_net_id': bart_parameters['public_net_id'],
    'private_mgmt_net_id': bart_parameters['private_mgmt_net_id'],
    'private_net_a_id': bart_parameters['private_net_a_id'],
    'private_net_d_id': bart_parameters['private_net_d_id'],
    'dnsaas_ip_address': bart_parameters['dnsaas_ip_address'],
    'cidr_mgmt': bart_parameters['cidr_mgmt'],
    'gw_mgmt': bart_parameters['gw_mgmt'],
    'image': bart_parameters['image'],
    'mgmt_prefix': bart_parameters['mgmt_prefix']
}
