import grpc
from django.conf import settings
from proto import search_pb2, search_pb2_grpc


class SearchGrpcClient:

    def __init__(self, host=None, port=None):
        self.host = host or settings.GO_SERVICE_GRPC_HOST
        self.port = port or settings.GO_SERVICE_GRPC_PORT
        self.address = f"{self.host}:{self.port}"

    def _create_channel(self):
        return grpc.insecure_channel(self.address)

    def federated_search(self, query, max_results, platforms):
        with self._create_channel() as channel:
            stub = search_pb2_grpc.SearchServiceStub(channel)

            request = search_pb2.SearchRequest(
                query=query,
                max_results=max_results,
                platforms=platforms
            )

            try:
                response = stub.FederatedSearch(request, timeout=5.0)
                return response
            except grpc.RpcError as e:
                raise Exception(f"gRPC call failed: {e.details()}")

    def health_check(self):
        with self._create_channel() as channel:
            stub = search_pb2_grpc.SearchServiceStub(channel)

            request = search_pb2.HealthCheckRequest()

            try:
                response = stub.HealthCheck(request, timeout=2.0)
                return response
            except grpc.RpcError as e:
                raise Exception(f"Health check failed: {e.details()}")
