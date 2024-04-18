#!/usr/bin/env python
# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import json
from opensearch_sdk_py.rest.extension_rest_handler import ExtensionRestHandler
from opensearch_sdk_py.rest.extension_rest_request import ExtensionRestRequest
from opensearch_sdk_py.rest.extension_rest_response import ExtensionRestResponse
from opensearch_sdk_py.rest.named_route import NamedRoute
from opensearch_sdk_py.rest.rest_method import RestMethod
from opensearch_sdk_py.rest.rest_status import RestStatus

class NeuralSparseSearchHandler(ExtensionRestHandler):
    def __init__(self, index=None, model_id=None, embedding_field=None):
        self.index = index
        self.model_id = model_id
        self.embedding_field = embedding_field

    def handle_request(self, rest_request: ExtensionRestRequest) -> ExtensionRestResponse:
        query_text = rest_request.param("query_text")
        if not self.embedding_field or not self.model_id:
            return ExtensionRestResponse(
                rest_request,
                RestStatus.BAD_REQUEST,
                bytes("Both 'embedding_field' and 'model_id' must be provided.", "utf-8")
            )

        query_body = self.build_query(query_text)
        response = self.execute_search(query_body)
        return ExtensionRestResponse(rest_request, RestStatus.OK, bytes(json.dumps(response), "utf-8"))

    def build_query(self, query_text):
        return {
            "query": {
                "neural_sparse": {
                    self.embedding_field: {
                        "query_text": query_text,
                        "model_id": self.model_id
                    }
                }
            }
        }

    def execute_search(self, query):
        # Mock-up: this function should interact with OpenSearch to perform the search
        return {"result": "search results"}

    @property
    def routes(self) -> list[NamedRoute]:
        return [
            NamedRoute(method=RestMethod.POST, path="/neural-sparse-search", unique_name="neural_sparse_search")
        ]
