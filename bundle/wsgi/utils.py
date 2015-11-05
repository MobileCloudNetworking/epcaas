# Copyright (c) 2014, Telecom Italia SpA

"""
Service Orchestrator for OpenEPC.
MCN 2014
"""

__author__ = '00917777'


"""
key_list = ['mcn.endpoint.pgwu-sgwu-1',
            'mcn.endpoint.mme-pgwc-sgwc',
            'mcn.endpoint.nat',
            'pgwu-sgwu-1.net_a.ip',
            'pgwu-sgwu-1.net_d.ip',
            'mme-pgwc-sgwc.net_d.ip',
            'nat.net_a.ip']
"""


# stack_state, stack_id, output = self.state()
def get_output_keys(output):
    key_list = []
    for item in output:
        key_list.append(item['output_key'])
    return key_list


# stack_state, stack_id, output = self.state()
def get_ips(output, key_name):
    # example key_name 'pgwu-sgwu-1.net_a.ip'
    for item in output:
        if item['output_key'] == key_name:
            ipadd = item['output_value'][0]['ip_address']
            # ending_number = ipadd.split('.')[3]
            return ipadd


# stack_state, stack_id, output = self.state()
def get_ip(output, key_name):
    # example key_name 'pgwu-sgwu-1.net_a.ip'
    for item in output:
        if item['output_key'] == key_name:
            ipadd = item['output_value']
            # ending_number = ipadd.split('.')[3]
            return ipadd

# stack_state, stack_id, output = self.state()
def get_fip(output, key_name):
    # example key_name 'mcn.endpoint.nat', when it is a FloatingIP
    """
    Gets the Floating IP of an endpoint, using the output dict returned
    by Heat. NOTE: the heat template
    must be written to return floating IP of VMs in the output. Note: this
    function only works for retrieveing Floating IPs; for IP addresses of
    other interfaces, you should use get_ips()

    :param key_name: the endpoint name (i.e. name used in SM definition)

    :return: Floating IP of the endpoint

    """
    for item in output:
        if item['output_key'] == key_name:
            return item['output_value']
