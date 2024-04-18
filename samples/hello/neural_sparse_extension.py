#!/usr/bin/env python
# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

from opensearch_sdk_py.extension import Extension
from opensearch_sdk_py.api.action_extension import ActionExtension
from opensearch_sdk_py.rest.extension_rest_handler import ExtensionRestHandler
from neural_sparse_handler import NeuralSparseSearchHandler

class NeuralSparseSearchExtension(Extension, ActionExtension):
    def __init__(self):
        super().__init__("neural-sparse-search")
        ActionExtension.__init__(self)

    @property
    def rest_handlers(self) -> list[ExtensionRestHandler]:
        return [NeuralSparseSearchHandler()]
