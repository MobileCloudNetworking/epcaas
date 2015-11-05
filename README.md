# EPC Service Manager

This depends upon:

* the [EPC SO](https://git.mobile-cloud-networking.eu/epcserviceorchestrator/mcn_epc_so/tree/master)
* the MCN [SM framework](https://git.mobile-cloud-networking.eu/cloudcontroller/mcn_sm/tree/initial_sm_impl)
  * see documentation here

## Development

Get the source:

    $ git clone git@git.mobile-cloud-networking.eu:edmo/epc-sm.git --recursive

Note the `--recursive` flag. This will get the submodule, the [EPC SO](https://git.mobile-cloud-networking.eu/epcserviceorchestrator/mcn_epc_so/tree/master).

### Dependencies
You will need to:

    $ pip install requests pyssf

and:

    $ git clone git@git.mobile-cloud-networking.eu:cloudcontroller/mcn_sm.git
    $ cd mcn_sm
    $ python ./setup install

## Configuration
See: `./etc/sm.cfg`

Make sure to provide a valid RSA SSH key. DSS keys are not supported.

## Running
Execute this:

    $ service_manager -c etc/sm.cfg
