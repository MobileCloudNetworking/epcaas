# MCN EPCaaS Service Orchestrator

The code for the MCN EPCaaS SO is contained in the wsgi/ dicrectory. The code is mainly contained in so.py 

## Testing EPC SO

Pre-requisites:
1. The mcn_epc_so repo should be installed on a Openstack controller, with HEAT and python-heatclient correctly installed *and working*. Please, check this by using the 'test.yaml' example, or 'hello_world.yaml' with the right values (see below), to instantiate a stack from the CLI, before using the EPCSO
2. The MCN Cloud Controller SDK must be installed on the same host of the SO. Do this by cloning git repository https://git.mobile-cloud-networking.eu/cloudcontroller/mcn_cc_sdk. 
3. Setup mcn_cc_sdk in a virtualenv (following instructions have been taken from misc/sample_so in mcn_cc_sdk repo)

Goto the directory of mcn_cc_sdk & setup virtenv:

    $ virtualenv /tmp/mcn_test_virt
    $ source /tmp/mcn_test_virt/bin/activate

Install SDK and required packages:

    $ pip install bottle pbr six iso8601 babel requests python-heatclient python-keystoneclient
    $ python setup.py install

Run EPC SO (again, as also described in mcn_cc_sdk, misc/sample_so)

    $ cd <path to SO>
    $ export OPENSHIFT_PYTHON_DIR=/tmp/mcn_test_virt
    $ export OPENSHIFT_REPO_DIR=<path to SO>
    $ python ./wsgi/application

The application now runs as a WSGI application on a simple HTTP server, answering on port 8051 (check out proxy configuration, if any). 

In a new terminal do get a token from keystone (token must belong to a user which has the admin role for the tenant):

    $ keystone token-get
    $ export KID='...'

Note 1: to get authentication token from keystone it is assumed OS_USERNAME, OS_PASSWORD and OS_TENANT_NAME are defined on the Openstack controller.

You can now visit the EPC SO interface at [here](localhost:8051):

    $ curl -X POST localhost:8051/action=init -H 'X-Auth-Token: '$KID -H 'X-Tenant-Name: '$OS_TENANT_NAME
    $ curl -X GET localhost:8051/
    $ curl -X GET localhost:8051/state
    $ curl -X POST localhost:8051/action=start  # to start SO decision logic

Two methods have been added to be used by SM

    $ curl -X POST localhost:8051/action=deploy # to simply deploy the STG (no runtime SO logic)
    $ curl -X POST localhost:8051/action=dispose  # disposes the STG

The order of calls to start the SOD decision logic should be:
- init (it creates the EPCSO() object and initializes it with the Keystone authentication token)
- start (it starts the EPCSODecision() logic, which in this release, just deploys the STG, contained in the data as an Heat template, and answers to state requests for 100 seconds and the dispose it)
- state (it queries the state of the service deployed)

After the service has been disposed, a new 'init' must be issued to re-create EPCSO().

## Documentation

To generate API documentation, go to doc/ directory and:

    $ export OPENSHIFT_PYTHON_DIR=/tmp/mcn_test_virt
    $ export OPENSHIFT_REPO_DIR=<path to SO>
      	     -- NEEDED TO CORRECTLY GENERATE DOCS
    $ make clean
    $ make html

You can find now the documentation in _build/html directory under doc/

## HEAT Template
Every valid and working Heat template can be used to test the EPCSO. In this release, the template must be put in the “data/” directory (of the EPC SO Bundle) and called “stg.yaml”. If you want to use the exemplary “stg.yaml”, please consider that it contains some hardcoded values, that have been used to speed up testing. Those values MUST be changed according your local environment:
- key_name
- image
- networks ("network" must be a network name, defined for the tenant you are using for testing and "uuid" must be its Network ID, as returned by Neutron)
