# EPCaaS Service Orchestrator

This is the implementation of a Service Orchestrator (SO) for the life-cycle management of an instance of OpenEPC (by Fraunhofer FOKUS). 

The SO adheres to MCN framework.

The bundle/data folder contains the HEAT templates, used by the SO to create proper 

### Dependencies

* the MCN [SM framework](https://git.mobile-cloud-networking.eu:cloudcontroller/mcn_sm.git)
  
You will need to:

    $ git clone git@git.mobile-cloud-networking.eu:cloudcontroller/mcn_sm.git
    $ cd mcn_sm
    $ python ./setup install

## Configuration
See: `./etc/sm.cfg`

Make sure to provide a valid RSA SSH key. DSS keys are not supported.

## Running
Execute this on the SM container/VM:

    $ service_manager -c etc/sm.cfg