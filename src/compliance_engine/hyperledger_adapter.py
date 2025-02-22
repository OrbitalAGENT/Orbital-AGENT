# orbital-agent/src/compliance_engine/hyperledger_adapter.py
import logging
import json
from hfc.fabric import Client
from hfc.fabric.user import User
from hfc.fabric.peer import Peer
from hfc.util import utils
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class LedgerError(Exception):
    """Base exception for Hyperledger Fabric interactions"""

class HyperledgerConnector:
    def __init__(self, network_profile: str, org_name: str, user_name: str):
        self.client = Client(net_profile=network_profile)
        self.org_name = org_name
        self.user_name = user_name
        self._configure_peers()
        
    def _configure_peers(self):
        """Initialize peer nodes from network configuration"""
        org_info = self.client.get_organization(self.org_name)
        self.peers = [
            Peer(endpoint=peer['url'], 
                 tls_cacerts=peer['tls_cacerts'],
                 opts={'grpc.ssl_target_name_override': peer['grpc_options']['ssl_target_name_override']})
            for peer in org_info['peers']
        ]

    async def submit_transaction(self, channel: str, cc_name: str, fcn: str, args: list) -> dict:
        """Submit transaction to Hyperledger Fabric network"""
        user = self._get_user_context()
        try:
            response = await self.client.chaincode_invoke(
                requestor=user,
                channel_name=channel,
                peers=self.peers,
                args=args,
                cc_name=cc_name,
                fcn=fcn,
                wait_for_event=True
            )
            return self._process_response(response)
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise LedgerError("Chaincode invocation failed") from e

    async def query_chaincode(self, channel: str, cc_name: str, fcn: str, args: list) -> dict:
        """Query data from blockchain ledger"""
        user = self._get_user_context()
        try:
            response = await self.client.chaincode_query(
                requestor=user,
                channel_name=channel,
                peers=self.peers,
                args=args,
                cc_name=cc_name,
                fcn=fcn
            )
            return self._parse_query_result(response)
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            raise LedgerError("Chaincode query failed") from e

    def _get_user_context(self) -> User:
        """Load user cryptographic materials"""
        org = self.client.get_organization(self.org_name)
        crypto_path = Path(org['crypto_path'])
        
        cert_path = crypto_path / 'users' / self.user_name / 'msp' / 'signcerts' / f'{self.user_name}cert.pem'
        key_dir = crypto_path / 'users' / self.user_name / 'msp' / 'keystore'
        key_path = next(key_dir.glob('*_sk'))
        
        return User(
            name=self.user_name,
            crypto=utils.Crypto(cert_path, key_path)
        )

    def _process_response(self, response: dict) -> dict:
        """Validate and parse transaction response"""
        if response['status'] != 'SUCCESS':
            error_msg = response.get('message', 'Unknown error')
            raise LedgerError(f"Transaction error: {error_msg}")
        
        return {
            'tx_id': response['tx_id'],
            'block_number': response['block_number'],
            'validation_code': response['validation_code']
        }

    def _parse_query_result(self, response: bytes) -> dict:
        """Handle query response parsing"""
        try:
            result = json.loads(response.decode('utf-8'))
            if isinstance(result, dict):
                return result
            return {'result': result}
        except json.JSONDecodeError:
            return {'raw_response': response.decode('utf-8')}

class ChaincodeManager:
    def __init__(self, connector: HyperledgerConnector):
        self.connector = connector
        self.channel_name = "orbital-channel"
        self.cc_name = "orbital-chaincode"
        
    async def record_operation(self, operation_data: dict) -> dict:
        """Store operation metadata on blockchain"""
        return await self.connector.submit_transaction(
            channel=self.channel_name,
            cc_name=self.cc_name,
            fcn="CreateOperation",
            args=[json.dumps(operation_data)]
        )

    async def verify_audit_trail(self, operation_id: str) -> dict:
        """Retrieve and validate audit trail"""
        return await self.connector.query_chaincode(
            channel=self.channel_name,
            cc_name=self.cc_name,
            fcn="QueryOperation",
            args=[operation_id]
        )
