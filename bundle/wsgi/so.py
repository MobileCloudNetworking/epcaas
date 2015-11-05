# Copyright (c) 2014, Telecom Italia SpA

"""
Service Orchestrator for OpenEPC.
MCN 2014
"""

__author__ = 'sruffino'

import logging
import os
import time
import threading
import epc_monitor
import epc_config

from sdk.mcn import util
from utils import get_fip
from globals import *
from pprint import pprint
from sm.so import service_orchestrator
from sm.so.service_orchestrator import LOG
from sm.so.service_orchestrator import BUNDLE_DIR

SO_DIR = BUNDLE_DIR


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


class PolicyEngine(object):
    """
    Handles external rule engine
    """

    def __init__(self):
        """
        docstring stub
        """
        self.rule_db = None

    def match_rule(self, value_dict, sic_type=''):
        """
        Matches a rule and takes a decision (e.g. scale out, scale in)
        based on that.
        """
        # print value_dict
        # ust do smtg with self.rule_db
        if self.rule_db is not None:
            pass

        if sic_type == 'MME':
            if value_dict[ATTCH_USERS] is not None and float(
                    value_dict[ATTCH_USERS]) > TSO_ATTCH_USERS:
                return 'SCALEOUT'
        if sic_type == 'MME':
            if value_dict[ATTCH_USERS] is not None and float(
                    value_dict[ATTCH_USERS]) < TSI_ATTCH_USERS:
                return 'SCALEIN'

        # Currently ignored
        if sic_type == 'GW':
            if value_dict[CPU_LOAD] is not None and float(
                    value_dict[CPU_LOAD]) > TSI_CPU_LOAD:
                return 'SCALEIN'

        # other sic type and metrics go here

        return 'NOOP'

    def list_rules(self):
        pass


class STG(object):
    """
    Retrieve, store and update TEMPLATE Instance graph, i.e. HOT template.
    Initialize the STG object, reading STG from HOT template file
    The template file will be included in the SO bundle.
    """

    def __init__(self):
        """
        docstring stub
        """
        try:
            # Load the initial heat template
            # TODO replace with dynamic template generation

            if TESTING_TILAB:
                templ_file = open(
                    os.path.join(SO_DIR, 'data', 'maas-test-tilab-1.yaml'),
                    'r')
            else:
                # templ_file = open(os.path.join(
                #     SO_DIR, 'data', 'epc-demo-review-1-gw-dns.yaml'), 'r')
                templ_file = open(os.path.join(
                    SO_DIR, 'data', 'epc-y3-1-gw-fixed-addressing-update.yaml'), 'r')
# tf = open(os.path.join(SO_DIR, 'data', 'maas-test-bart-1-deploy.yaml'), 'r')
# tf = open(os.path.join(SO_DIR, 'data', 'epc-demo-review-1-gw.yaml'), 'r')

            self.graph = templ_file.read()
            templ_file.close()
        except IOError:
            LOG.debug('File not found')

    def get(self):
        """
        Returns the STG
        """
        return self.graph

    def set(self, graph):
        """
        Updates the STG with a new HEAT template.
        The template should be already read from file

        :param graph: the template read from file

        """
        self.graph = graph


class SIG(object):
    """
    Stores and update current Instance graph. CURRENTLY NOT USED.
    """

    def __init__(self):
        """
        docstring stub
        """
        self.graph = None

    def read(self):
        """
        Read he SIG object
        """
        return self.graph

    def update(self):
        """
        Calls proper CC method to retrieve
        the updated state of the service instance
        """
        pass


# XXX you may have to implement some very simple stub methods that just have `pass` as their implementation

class EPCSODecision(service_orchestrator.Decision, threading.Thread):
    """
    EPC SOD contains the logic of the SO in an infinite loop

    :param so_e: EPCSOExecution() object, used to send commands to Cloud
        Controller

    :param token: Keystone authorization token, needed to authenticate
        with Openstack

    :param ready_event: threading event, set by EPCSOexecution, used to
        signal the completion of the provision step

    :param stop_event: threading event, set by EPCSOexecution, used to
        signal a call to dispose method. The event is checked wvery 10 s;
        if this event is set, EPCSOdecision thread stops.

    """

    def __init__(self, so_e, token, tenant_name, ready_event, stop_event):
        # super(EPCSODecision, self).__init__(so_e, token, tenant_name)
        service_orchestrator.Decision.__init__(self, so_e, token, tenant_name)
        threading.Thread.__init__(self)

        self.ready_event = ready_event
        self.stop_event = stop_event
        self.so_e = so_e
        self.token = token

        self.pol_eng = PolicyEngine()

        self.scaling_allowed = True

        # self.scaleout_triggered = True
        # self.scaleout_success = True
        # self.scalein_triggered = True
        # self.scalein_success = True

        # time.time() when last MME scaling (up/down) occured
        self.last_mme_scaling_time = 0
        # time.time() when last GW scaling (up/down) occured
        self.last_gw_scaling_time = 0

        self.num_of_mme = 1
        self.num_of_gw = 1

        LOG.debug('EPC SO Decision init')

    def run(self):
        """
        Start EPC SOD decision logic
        """

        LOG.debug('Waiting for deploy and provisioning to finish')
        self.ready_event.wait()
        LOG.debug('Starting runtime logic...')

        self.so_e.mme_monitor.create(
            maas_ip=self.so_e.sm_parameters['maas_ip_address'])
        self.so_e.gw_monitor.create(
            maas_ip=self.so_e.sm_parameters['maas_ip_address'])

        # it'll be the OpenEPC MME host name,
        # must be aligned with heat template
        vm_name = MME_VM_NAME

        # RUN-TIME MANAGEMENT
        while not self.stop_event.isSet():
            # LOG.debug('wait_for_event_timeout starting')
            event_is_set = self.stop_event.wait(10)
            # LOG.debug('event set: %s', event_is_set)

            if event_is_set:
                LOG.debug('STOP event set after disposal')
            else:
                # LOG.debug('stop event not set')
                # core decision logic loop goes here

                stack_state, stack_id, output = self.so_e.state()
                pprint(output)
                # NOTE: add controls here that checks the status of the stack.
                # so that it can wait until and update_complete,
                # before updating the num_gw

                # Retrieve values of the metrics from MaaS; in this version,
                # it retrieves values from MME

                mme_values = self.so_e.mme_monitor.get(vm_name)
                for m in self.so_e.mme_monitor.metrics:
                    print METRICS[m] + ':',
                    print mme_values[m],
                    print ''

                # print self.so_e.gw_monitor.metrics
                # Currently ignored
                gw_values = self.so_e.gw_monitor.get(vm_name)
                # print gw_values

                # Check actions in the Policy Engine
                action_mme = self.pol_eng.match_rule(mme_values, 'MME')
                # Currently ignored
                action_gw = self.pol_eng.match_rule(gw_values, 'GW')

                # Check if scaling is allowed at this moment
                if self.last_gw_scaling_time == 0:
                    diff = 0
                else:
                    diff = int(time.time() - self.last_gw_scaling_time)
                if diff > SCALING_GUARD_TIME or self.last_gw_scaling_time == 0:
                    self.scaling_allowed = True

                LOG.debug('SCALING ALLOWED: ' + str(self.scaling_allowed))

                # NOTE: uncomment, when using MaaS to retrieve the value
                # self.num_of_gw = mme_values[NUM_SWITCHES]
                # print "Current # of SW: " + self.num_of_gw

                # Check if the scaling conditions are met
                # and activate scaling accordingly
                if action_mme == 'SCALEOUT' and \
                        self.scaling_allowed and self.num_of_gw < 2:
                    if TESTING_TILAB:
                        templ_file = open(os.path.join(
                            SO_DIR, 'data',
                            'maas-test-tilab-2.yaml'), 'r')
                    else:
                        # templ_file = open(os.path.join(
                        #     SO_DIR, 'data',
                        #     'epc-demo-review-2-gw-dns.yaml'), 'r')
                        templ_file = open(os.path.join(
                            SO_DIR, 'data',
                            'maas-test-bart-2-deploy.yaml'), 'r')                        
# tf = open(os.path.join(SO_DIR, 'data', 'epc-demo-review-2-gw.yaml'), 'r')
                    try:
                        self.so_e.stg.set(templ_file.read())
                        templ_file.close()
                    except IOError:
                        LOG.debug('File not found')
                    self.so_e.internal_update()
                    self.last_gw_scaling_time = time.time()
                    # NOTE: comment the following line, when using state()
                    # to retrieve the value
                    self.num_of_gw += 1

                    self.scaling_allowed = False

                if action_mme == 'SCALEIN' and \
                        self.scaling_allowed and self.num_of_gw > 1:

                    # Signal PGW 2 to stop pgwu-sgwu service
                    LOG.debug('SHUTTING DOWN PGW2')
                    # only if using FloatingIPs we are able to ssh in
                    # pgw2 to shut it down
                    if USE_FIP_FOR_VMs:
                        stack_state, stack_id, output = self.so_e.state()
                        pgw2_fip = get_fip(output, PGW2_ENDPOINT)
                        if pgw2_fip is not None:
                            print 'PGW2 IP: ' + pgw2_fip
                            self.so_e.epcConfig.shutdown_pgw(
                                pgw_ipaddress=pgw2_fip)
                        else:
                            LOG.debug(
                                'PGW2 not found. Scale-in triggered before '
                                'scale-out completion?')

                    # Update the stack, back to one SW only
                    if TESTING_TILAB:
                        templ_file = open(os.path.join(
                            SO_DIR, 'data',
                            'maas-test-tilab-1.yaml'), 'r')
                    else:
                        templ_file = open(os.path.join(
                            SO_DIR, 'data',
                            'epc-demo-review-1-gw-dns.yaml'), 'r')
# tf = open(os.path.join(SO_DIR, 'data', 'epc-demo-review-1-gw.yaml'), 'r')
                    try:
                        self.so_e.stg.set(templ_file.read())
                        templ_file.close()
                    except IOError:
                        LOG.debug('File not found')
                    self.so_e.internal_update()
                    self.last_gw_scaling_time = time.time()
                    # NOTE: comment the following line,
                    # when using state() to retrieve the value
                    self.num_of_gw -= 1
                    self.scaling_allowed = False

                if action_gw == 'SCALEOUT':
                    pass

        LOG.debug('SOD thread stopped')

        # Delete the hosts on the MaaS (clean up)
        if self.so_e.mme_monitor.delete_host(MME_VM_NAME) == 0:
            LOG.debug('Host ' + MME_VM_NAME + ' deleted successfully from MaaS')
        if self.so_e.mme_monitor.delete_host(PGW1_VM_NAME) == 0:
            LOG.debug('Host ' + PGW1_VM_NAME + ' deleted successfully from MaaS')
        if self.so_e.mme_monitor.delete_host(NAT_VM_NAME) == 0:
            LOG.debug('Host ' + NAT_VM_NAME + ' deleted successfully from MaaS')
        # The following call can fail, if pgw2 is not present (e.g. if scale-out
        # was never triggered)
        if self.so_e.mme_monitor.delete_host(PGW2_VM_NAME) == 0:
            LOG.debug('Host ' + PGW2_VM_NAME + ' deleted successfully from MaaS')

    def stop(self):
        """
        Stops EOC SOD decision logic
        """
        pass


# XXX you may have to implement some very simple stub methods that just have `pass` as their implementation
#
class EPCSOExecution(service_orchestrator.Execution):
    """
    Interface to the CC methods. No decision is taken here on the service

    :param token: Keystone authorization token, needed to talk
        with Openstack

    :param tenant_name: Tenant name

    :param region_name: Region to deploy the service (it can be UBern
    or RegionOne, i.e. bart)

    :param ready_event: threading event, used to
        signal the completion of the provision step to the
        EPCSOdecision

    :param stop_event: threading event, used to
        signal a call to dispose method. The event is checked every 10 s;
        if this event is set, EPCSOdecision thread stops.
    """

    def __init__(self, token, tenant_name, ready_event, stop_event,
                 region_name=DEFAULT_REGION):
        """
        docstring stub
        """
        # super(EPCSOExecution, self).__init__(token, tenant_name)
        service_orchestrator.Execution.__init__(self, token, tenant_name)
        self.token = token
        self.tenant_name = tenant_name
        if region_name is not None and region_name != '':
            self.region_name = region_name

        self.event = ready_event  # update finished
        self.stop_event = stop_event  # disposal method called
        self.stack_id = None
        self.stg = STG()
        self.epc_config = epc_config.EPCConfig()
        self.mme_monitor = epc_monitor.MMEMonitor()
        self.gw_monitor = epc_monitor.GWMonitor()
        self.maas = None
        self.dnsaas = None

        if self.region_name == 'UBern':
            # heat_parameters contains the parameters passed to heat
            self.heat_parameters = ubern_heat_parameters
            self.conf_param = {
                'conf_proxy': ubern_parameters['conf_proxy'],
                'cidr_float': ubern_parameters['cidr_float'],
                'gw_mgmt': ubern_parameters['gw_mgmt']
            }
        elif self.region_name == 'RegionOne':
            self.heat_parameters = bart_heat_parameters
            # os.environ['http_proxy'] = bart_parameters['conf_proxy']
            self.conf_param = {
                'conf_proxy': bart_parameters['conf_proxy'],
                'cidr_float': bart_parameters['cidr_float'],
                'gw_mgmt': bart_parameters['gw_mgmt']
            }

        self.sm_parameters = {}  # Contains parameters passed by SM

        LOG.debug('EPC SO Execution init')
        self.deployer = util.get_deployer(self.token, url_type='public',
                                          tenant_name=self.tenant_name,
                                          region=self.region_name)

    def design(self):
        """
        STUB: placeholder for a future design() method implementation
        (if needed)
        """
        LOG.debug('EPC SOE Executing design logic')

    def deploy(self, attributes):
        """
        Deploys an STG in the form of an HOT template.
        It can be called directly, and also through the SOD.

        :param attributes OCCI attributes passed by SM. Must match the
        attributes definition of the service in the SM. E.g. in this way the
        SM can pass to a SO parameters to be used in the config call. This
        is useful when an higher level SM, e.g. an E2E SM, manages also one
        or more support services, like DNSaaS or MaaS. The E2E SM will pass
        the EPCaaS SM the relevant parameters of the support services,
        like e.g. IP address for managing a MaaS.
        """

        LOG.debug('Executing deploy logic')

        if attributes:
            LOG.debug('EPC SO deployment - attributes')
            print attributes

            # MAAS and DNSAAS
            # Even if MaaS and DNSaaS ip addresses are passed
            # during deployment, it is ignored, since it is used only
            # during update, when the SICs are configured

        # Start creation of stack
        template = self.stg.get()

        LOG.debug('Executing deployment logic')
        if self.stack_id is None:
            self.stack_id = self.deployer.deploy(
                template, self.token,
                parameters=self.heat_parameters, region_name=self.region_name)
        else:
            LOG.debug('Error: calling deploy on existing stack')
            return

    def provision(self, attributes):
        """
        Takes care of the provisioning of a deployed instance of OpenEPC
        It calls the service-specific, implementation-specific method to
        actually configure service parameters on the SIC

        :param attributes: OCCI attributes passed by SM. Must match the
            attributes definition of the service in the SM. E.g. in this way
            the SM can pass to a SO parameters to be used in the config call.
            This
            is useful when an higher level SM, e.g. an E2E SM, manages also one
            or more support services, like DNSaaS or MaaS. The E2E SM will pass
            the EPCaaS SM the relevant parameters of the support services,
            like e.g. IP address for managing a MaaS.

        """

        # SR 16/6/2015: currently empty,
        # since the epcaas VMs will be configured when the MaaS and DNSaaS ip
        # addresses will be available, namely when update is called from the
        # SM.

        LOG.debug('Executing provisioning logic')
        # NOTE: change this when real params are passed to config
        # parameters = attributes
        #if self.epc_config.config(parameters=parameters) != 0:
        #    LOG.debug('Provisioning failed')
        pass

    def dispose(self):
        """
        Dispose all SICs of a stack deployed.
        """

        LOG.debug('Executing disposal logic')

        # stack_state, stack_id, output = self.state()

        # Dispose Maas, if created
        if self.maas is not None:
            LOG.debug('Disposing MaaS')
            util.dispose_maas(self.token, self.maas)

        # Dispose DNSaaS, if created
        if self.dnsaas is not None:
            LOG.debug('Disposing DNSaaS')
            util.dispose_dnsaas(self.token, self.dnsaas)

        # Dispose heat stack
        if self.stack_id is not None:
            self.deployer.dispose(self.stack_id, self.token)
            self.stack_id = None

            # on disposal, the SOE should notify the SOD to shutdown its thread
            self.stop_event.set()

    def state(self):
        """
        Get the current state of a stack, if deployed
        """
        LOG.debug('Executing state retrieval logic')
        if self.stack_id is not None:
            tmp = self.deployer.details(self.stack_id, self.token)

            try:
                output = tmp['output']
                LOG.debug('State: ' + tmp['state'])
                return tmp['state'], self.stack_id, output
            except KeyError:
                # LOG.debug('************* KeyError raised ****************')
                return tmp['state'], self.stack_id, ''
        else:
            return 'Unknown', 'N/A', ''
            # SR: hack for demo 9/2/2015
            # this means that SO cannot wait for stack creation or update
            # return 'CREATE_COMPLETE', 'N/A', ''

    def update(self, attributes):
        """
        It configures a running EPCaaS using parameters passed by SM.

        :param attributes: is a dict that contains the OCCI attributes passed
            by SM (X-OCCI-ATTRIBUTE)

        """

        LOG.debug('Executing update/provisioning logic')

        stack_state, stack_id, output = self.state()

        if not (stack_state == 'CREATE_COMPLETE' or
                stack_state == 'UPDATE_COMPLETE'):
            LOG.debug('Stack is not in a stable state a.t.m.. Retry')
            return False

        confg = Configurator(token=self.token, tenant=self.tenant_name, region=self.region_name,
                             sm_parameters=self.sm_parameters, conf_param=self.conf_param, attributes=attributes,
                             epc_config=self.epc_config, output=output, event=self.event)
        # XXX no management of this thread is done
        confg.start()

    def internal_update(self):
        """
        It updates a running Heat stack by sending a new template
        """
        LOG.debug('Executing internal update logic')

        template = self.stg.get()
        if self.stack_id is not None:
            self.deployer.update(self.stack_id, template, self.token,
                                 parameters=self.heat_parameters)
        '''
        # Wait until CREATE_COMPLETE or UPDATE_COMPLETE
        stack_state = 'Unknown'
        while not (stack_state == 'CREATE_COMPLETE' or
                   stack_state == 'UPDATE_COMPLETE'):
            time.sleep(5)
            stack_state, stack_id, output = self.state()
        '''


class Configurator(threading.Thread):

    def __init__(self, token, tenant, region, sm_parameters, conf_param, attributes, epc_config, output, event):
        super(Configurator, self).__init__()
        self.attributes = attributes
        self.sm_parameters = sm_parameters
        self.conf_param = conf_param
        self.token = token
        self.tenant_name = tenant
        self.region_name = region
        self.epc_config = epc_config
        self.output = output
        self.event = event
        self.dnsaas = None

    def run(self):

        if self.attributes:
            LOG.debug('EPC SO update - attributes')
            print self.attributes
        else:
            LOG.debug('EPC SO update - EMPTY ATTRIBUTES')
            self.attributes = []  # to avoid error later

        # SR 07/15: MaaS and DNSaaS support
        # The selection logic for MaaS and DNSaaS is straightforward:
        # if MaaS and DNSaaS IPs are passed to the SM, use those
        # (please note that if this is the case, they must be
        # preconfigured, because SO has no mean to use MCN CC APIs
        # unless it creates the objects)
        # If not, create MaaS and DNSaaS with MCN CC API and
        # possibly configure them.
        # If creation and configuration is unsuccessful, use
        # pre-provisioned MaaS and DNS VMs (IPs must be put in globals.py)
        # as fallback

        # MAAS
        # XXX should be supplied from the external
        if 'mcn.endpoint.maas' in self.attributes:
            LOG.debug('MaaS address in attributes')
            self.sm_parameters['maas_ip_address'] = self.attributes['mcn.endpoint.maas']
        else:
            LOG.debug('MaaS address NOT in attributes - Failing')
            raise RuntimeError('MaaS address NOT in attributes - Failing')

        # DNSAAS
        # XXX Should be supplied from the external
        if 'mcn.endpoint.api' in self.attributes:
            LOG.debug('DNSaaS address in attributes')
            self.sm_parameters['dnsaas_ip_address'] = self.attributes['mcn.endpoint.api']
            # TODO create a DNS client here based on the IP address supplied through the update call
            # how is done usually? master copy doesn't show
        else:
            LOG.debug('DNSaaS address NOT in attributes - Failing')
            raise RuntimeError('MaaS address NOT in attributes - Failing')

        # Configuring EPCaaS SICs with parameters passed by SM
        LOG.debug('Executing provisioning logic of OpenEPC')
        ret_code = self.epc_config.config(self.sm_parameters, self.conf_param, self.output)
        if ret_code < 0:
            LOG.debug('EPC SO update - ERROR in CONFIGURATION of OpenEPC. Code: ' + ret_code)
            return False

        # we should not execute this if a DNS Service IP is supplied
        if self.dnsaas is not None:  # if we used get_dnsaas above
            LOG.debug('Executing provisioning logic of DNSaaS')
            ret_code = self.epc_config.config_dnsaas(self.dnsaas, self.output, self.token)
            if ret_code < 0:
                LOG.debug('EPC SO update - ERROR in CONFIGURATION of DNSaaS '
                          'Code: ' + ret_code)
                return False

        # once provisioning is completed, update phase is done;
        # signal to EPCSODecision it can start
        LOG.debug('Before event.set()')
        self.event.set()
        LOG.debug('After event.set()')

class EPCSO(object):
    """
    EPC SO class which contains two objects: one SO-E and one SO-D,
    which in turn has a reference to the SO-E.

    :param token: the Keystone authorization token used to send commands
        to Openstack

    :param tenant_name: the Tenant name authorized by token

    """

    def __init__(self, token, tenant_name, region_name):
        """
        Initialize the EPC Service Orchestrator object.
        """

        # this python thread event is used to notify the SOD that the
        # runtime phase can execute its logic
        self.ready_event = threading.Event()
        # this python thread event is used to notify the SOD to stop runtime
        #  phase after a delete(and end the thread)
        self.stop_event = threading.Event()

        self.so_e = EPCSOExecution(token, tenant_name, self.ready_event,
                                   self.stop_event, region_name=region_name)
        self.so_d = EPCSODecision(self.so_e, token, tenant_name,
                                  self.ready_event,
                                  self.stop_event)
        LOG.debug('Starting SOD thread...')
        self.so_d.start()
