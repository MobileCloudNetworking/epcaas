# Copyright (c) 2014, Telecom Italia SpA

"""
Service Orchestrator for OpenEPC.
MCN 2014
"""
from globals import CPU_LOAD, ATTCH_USERS, NUM_SWITCHES, BW_OCC
from pyzabbix import ZabbixAPI
import traceback
# import sys

__author__ = '00917777'


class EPCMonitor(object):
    """
    It handles the connection to a Zabbix server; service specific monitors
    should be implemented as sub-classes (e.g. MMEMonitor, GWMonitor)
    """

    def __init__(self):
        """
        Initialize the EPCMonitor object
        """
        self.server = ''
        self.username = 'admin'     # default of zabbix server
        self.password = 'zabbix'    # default of zabbix server
        self.zapi = None

        self.__metrics = []

    @property
    def metrics(self):
        """
        Method to retrieve the metrics list, which contain a list of the
        available metrics for a certain service; metrics are coded according
        constant defined in globals.py (e.g. CPU_LOAD, etc.)
        :return: the metrics list
        """
        return self.__metrics

    @metrics.setter
    def metrics(self, value):
        """
        Method to set the available metrics for a certain service
        :param value: a list of constant values, which represent available
        metrics for the service. The constant values are defined in globals.py
        :return: Nothing
        """
        self.__metrics = value

    def get(self, host_name):
        """
        Retrieves the latest measured values, for all the metrics of a
        service; it cycle through the metrics included in the self.metrics list
        and calls self.get_value method for each of them, which actually
        gets the measurement from the Zabbix server.
        :param host_name: the IP address or hostname of the service to
        retrieve the metrics of.
        :return: measured values as a dict (one entry could be
        e.g. k,v = {'CPU_LOAD', 98.67})
        """
        measured_values = {}
        for metric in self.metrics:
            measured_values[metric] = self.get_value(metric, host_name)
        return measured_values

    def get_value(self, metric, host_name):
        """
        It retrieves the latest data for a given metric; :param metric: the
        name of the metric to retrieve, using constant names specified in
        globals.py;
        :param host_name: the IP address or hostname of the
        service to read the metrics
        :return: the retrieved value, if present.
        """
        raise NotImplementedError

    def create(self, maas_ip='127.0.0.1', maas_uid='admin', maas_pwd='zabbix'):
        """
        Initializes a connection to a Zabbix server; must be called before
        sending any other command to Zabbix, e.g. before retrieving metrics
        values
        :param maas_ip: the IP address of the Zabbix server to
        connect to
        :param maas_uid: defaults to admin, the UID used to login
        into Zabbix
        :param maas_pwd: defaults to zabbix, the PWD used to
        login into Zabbix
        :return:  Nothing
        """
        # Connect to MaaS
        self.server = 'http://' + maas_ip + '/zabbix'
        self.username = maas_uid
        self.password = maas_pwd

        # zabbix api
        self.zapi = ZabbixAPI(server=self.server)
        try:
            print '*** Connecting to MaaS'
            self.zapi.login(self.username, self.password)
            print '*** Connected to MaaS'
        except BaseException as exc:
            print '*** Caught exception: %s: %s' % (exc.__class__, exc)
            traceback.print_exc()
            # Avoid exit, if MaaS is not available
            # sys.exit(1)
            print('*** ERROR: MaaS connection failed. No monitoring and no '
                  'scaling available. Deploy continues ***')

    def delete_host(self, host_name):
        """
        Deletes an host definition from a Zabbix server; this method should
        be called at service disposal
        :param host_name: the hostname of the host to be deleted from Zabbix
        :return: Nothing
        """

        # gets hostid from hostname
        try:
            hostid = self.zapi.host.get(
                filter={"host": host_name})[0]["hostid"]
        except BaseException as exc:
            print '*** Caught exception: %s: %s' % (exc.__class__, exc)
            traceback.print_exc()
            print "WARNING: Hostname " + host_name + " not found"
            # TODO return somthing
            return 1

        # deletes hostid
        try:
            self.zapi.host.delete(hostid)
        except BaseException as exc:
            print '*** Caught exception: %s: %s' % (exc.__class__, exc)
            traceback.print_exc()
            print "ERROR: CANNOT DELETE THE HOST " + host_name
            # TODO return somthing
            return 1

        return 0


class MMEMonitor(EPCMonitor):
    """
    Monitor definition for an OpenEPC MME;
    Metrics: CPU_LOAD, ATTCH_USERS, NUM_SWITCHES
    """
    def __init__(self):
        """
        MMEMonitor init; sets the available metrics in the metrics list;
        This list is statically defined in this class, at the moment.
        The list shall contain only constants contained in globals.py
        :return: NA
        """
        super(MMEMonitor, self).__init__()
        self.metrics = [CPU_LOAD, ATTCH_USERS, NUM_SWITCHES]

    def get_value(self, metric, host_name):

        if metric == CPU_LOAD:
            key = "system.cpu.util[,idle]"

        if metric == ATTCH_USERS:
            # key = "system.cpu.util[,idle]"
            key = "attached.subs.gw"

        if metric == NUM_SWITCHES:
            # key = "system.cpu.util[,idle]"
            key = "attached.switch.gw"

        # Retrieve the metric and return its value
        try:
            hostid = self.zapi.host.get(
                filter={"host": host_name})[0]["hostid"]
        except BaseException as exc:
            print '*** Caught exception: %s: %s' % (exc.__class__, exc)
            print "WARNING: Hostname " + host_name + " not found"
            # TODO return somthing
            return

        try:
            value = self.zapi.item.get(
                host=host_name, filter={"key_": key})[0]["lastvalue"]
            return value
        except BaseException as exc:
            print '*** Caught exception: %s: %s' % (exc.__class__, exc)
            traceback.print_exc()
            print '*** ERROR: User metric not found ***'
            # TODO return somthing
            return


class GWMonitor(EPCMonitor):
    """
    Monitor definition for an OpenEPC GW;
    Metrics are TBD for this class
    """
    def __init__(self):
        super(GWMonitor, self).__init__()
        self.metrics = [CPU_LOAD, BW_OCC]

    def get_value(self, metric, host_name):

        if metric == CPU_LOAD:
            return 34.4

        if metric == BW_OCC:
            return 10232382
