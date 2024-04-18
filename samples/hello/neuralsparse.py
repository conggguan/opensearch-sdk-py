#!/usr/bin/env python
#
# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.
#

import logging

from neural_sparse_extension import NeuralSparseSearchExtension
from opensearch_sdk_py.server.async_extension_host import AsyncExtensionHost

logging.basicConfig(encoding="utf-8", level=logging.INFO)

# 创建 NeuralSparseSearchExtension 实例
extension = NeuralSparseSearchExtension()
logging.info(f"Starting {extension} that implements {extension.implemented_interfaces}.")

# 创建和配置 AsyncExtensionHost
host = AsyncExtensionHost(port=1234)
host.serve(extension)

logging.info(f"Listening on {host.address}:{host.port}.")
host.run()
