#!/usr/bin/env python
import asyncio
import logging
import socket

from opensearch_sdk_py.transport.discovery_node import DiscoveryNode
from opensearch_sdk_py.transport.discovery_node_role import DiscoveryNodeRole
from opensearch_sdk_py.transport.initialize_extension_request import (
    InitializeExtensionRequest,
)
from opensearch_sdk_py.transport.initialize_extension_response import (
    InitializeExtensionResponse,
)
from opensearch_sdk_py.transport.outbound_message import OutboundMessage
from opensearch_sdk_py.transport.outbound_message_request import OutboundMessageRequest
from opensearch_sdk_py.transport.outbound_message_response import (
    OutboundMessageResponse,
)
from opensearch_sdk_py.transport.stream_input import StreamInput
from opensearch_sdk_py.transport.stream_output import StreamOutput
from opensearch_sdk_py.transport.transport_address import TransportAddress
from opensearch_sdk_py.transport.transport_handshaker_handshake_request import (
    TransportHandshakerHandshakeRequest,
)
from opensearch_sdk_py.transport.transport_handshaker_handshake_response import (
    TransportHandshakerHandshakeResponse,
)
from opensearch_sdk_py.transport.transport_service_handshake_request import (
    TransportServiceHandshakeRequest,
)
from opensearch_sdk_py.transport.transport_service_handshake_response import (
    TransportServiceHandshakeResponse,
)


async def handle_connection(conn, loop):
    try:
        conn.setblocking(False)
        # out = StreamOutput(loop, conn)
        while raw := await loop.sock_recv(conn, 1024 * 10):
            input = StreamInput(raw)
            print(f"\nreceived {input}, {len(raw)} byte(s)\n\t#{str(raw)}")

            header = OutboundMessage().read_from(input)
            print(f"\t{header.tcp_header}")
            if (
                header.thread_context_struct.request_headers
                or header.thread_context_struct.response_headers
            ):
                print(f"\t{header.thread_context_struct}")

            if header.is_request():
                request = OutboundMessageRequest().read_from(input, header)
                if request.features:
                    print(f"\tfeatures: {request.features}")
                if request.action:
                    print(f"\taction: {request.action}")

                # TODO: Need a better way of matching these action names to reading their classes
                if request.action == "internal:tcp/handshake":
                    tcp_handshake = TransportHandshakerHandshakeRequest().read_from(
                        input
                    )
                    print(f"\topensearch_version: {tcp_handshake.version}")

                    response = OutboundMessageResponse(
                        request.thread_context_struct,
                        request.features,
                        TransportHandshakerHandshakeResponse(request.get_version()),
                        request.get_version(),
                        request.get_request_id(),
                        request.is_handshake(),
                        request.is_compress(),
                    )

                    output = StreamOutput()
                    response.write_to(output)

                    raw_out = output.getvalue()
                    print("\tparsed TCP handshake, returning a response")
                    print(
                        f"\nsent handshake response, {len(raw_out)} byte(s):\n\t#{raw_out}\n\t{response.tcp_header}"
                    )

                    await loop.sock_sendall(conn, output.getvalue())
                elif request.action == "internal:transport/handshake":
                    transport_handshake = (  # noqa: F841 we may want to access task_id
                        TransportServiceHandshakeRequest().read_from(input)
                    )

                    response = OutboundMessageResponse(
                        request.thread_context_struct,
                        request.features,
                        TransportServiceHandshakeResponse(
                            DiscoveryNode(
                                node_name="hello-world",
                                node_id="hello-world",
                                address=TransportAddress("127.0.0.1", 1234),
                                roles={
                                    DiscoveryNodeRole.CLUSTER_MANAGER_ROLE,
                                    DiscoveryNodeRole.DATA_ROLE,
                                    DiscoveryNodeRole.INGEST_ROLE,
                                    DiscoveryNodeRole.REMOTE_CLUSTER_CLIENT_ROLE,
                                },
                            )
                        ),
                        request.get_version(),
                        request.get_request_id(),
                        request.is_handshake(),
                        request.is_compress(),
                    )

                    output = StreamOutput()
                    response.write_to(output)

                    raw_out = output.getvalue()
                    print("\tparsed Transport handshake, returning a response")
                    print(
                        f"\nsent handshake response, {len(raw_out)} byte(s):\n\t#{raw_out}\n\t{response.tcp_header}"
                    )

                    await loop.sock_sendall(conn, output.getvalue())
                elif request.action == "internal:discovery/extensions":
                    initialize_extension_request = (
                        InitializeExtensionRequest().read_from(input)
                    )
                    print(
                        f"\tsource node: {initialize_extension_request.source_node.address.host_name}"
                        + f":{initialize_extension_request.source_node.address.port}"
                        + f", extension {initialize_extension_request.extension.address.host_name}"
                        + f":{initialize_extension_request.extension.address.port}"
                    )

                    # TODO: In reality a lot of other initialization work happens here.
                    # Skipping for now so that OpenSearch won't fail initialization.
                    #
                    # Sometime between tcp and transport handshakes and the eventual response,
                    # the uniqueId gets added to the thread context.
                    request.thread_context_struct.request_headers[
                        "extension_unique_id"
                    ] = "hello-world"

                    response = OutboundMessageResponse(
                        request.thread_context_struct,
                        request.features,
                        InitializeExtensionResponse(
                            "hello-world", ["Extension", "ActionExtension"]
                        ),
                        request.get_version(),
                        request.get_request_id(),
                        request.is_handshake(),
                        request.is_compress(),
                    )

                    output = StreamOutput()
                    response.write_to(output)

                    raw_out = output.getvalue()
                    print(
                        "\tparsed Extension initialization request, returning a response"
                    )
                    print(
                        f"\nsent init response, {len(raw_out)} byte(s):\n\t#{raw_out}\n\t{response.tcp_header}"
                    )

                else:
                    print(
                        f"\tparsed action {header.tcp_header}, haven't yet written what to do with it"
                    )
            else:
                print(
                    f"\tparsed {header.tcp_header}, this is a response to something I sent, haven't yet written what to do with it"
                )

    except Exception as ex:
        logging.exception(ex)
    finally:
        conn.close()


async def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 1234))
    server.setblocking(False)
    server.listen()

    loop = asyncio.get_event_loop()

    print(f"listening, {server}")
    while True:
        conn, _ = await loop.sock_accept(server)
        print(f"got a connection, {conn}")
        loop.create_task(handle_connection(conn, loop))


asyncio.run(run_server())
