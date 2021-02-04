#!/usr/bin/env python

import sys
from b2_connector import B2Connector

# Instantiate B2 connector
b2 = B2Connector()
b2.output_files_with_multiple_versions()
