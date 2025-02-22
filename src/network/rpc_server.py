# src/network/rpc_server.py
import logging
import grpc
from concurrent import futures
from typing import Any

class RPCService:
    def __init__(self, host: str = '0.0.0.0', port: int = 50051):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.address = f"{host}:{port}"
        
    def add_service(self, service: Any, handler: Any) -> None:
        service.add_to_server(self.server, handler())
        
    def start(self) -> None:
        self.server.add_insecure_port(self.address)
        self.server.start()
        logging.info(f"gRPC server started on {self.address}")
        
    def stop(self) -> None:
        self.server.stop(5)
        logging.info("gRPC server stopped")

# Example usage:
# from generated import agent_pb2_grpc, agent_pb2
# service = RPCService()
# service.add_service(agent_pb2_grpc.AgentServicer, AgentHandler)
# service.start()
