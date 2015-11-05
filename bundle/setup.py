#   Copyright (c) 2013-2015, Intel Performance Learning Solutions
#   Ltd, Intel Corporation.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Setuptools script.
"""

from setuptools import setup

setup(name='mcn_epc_so',
      version='0.1',
      description='EPCaaS SO',
      author='Telecom Italia S.p.A.',
      author_email='simone.ruffino@telecomitalia.it',
      url='http://www.telecomitalia.it',
      license='Apache 2.0',
      install_requires=['httplib2', 'paramiko'],
      packages=['wsgi'])
