# src/security/vault_integration.py
import hvac
import logging
from typing import Optional

class VaultManager:
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)
        
    def read_secret(self, path: str) -> Optional[dict]:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except hvac.exceptions.VaultError as e:
            logging.error(f"Vault error: {str(e)}")
            return None
            
    def create_token(self, policies: list, ttl: str = '1h') -> Optional[str]:
        try:
            response = self.client.auth.token.create(policies=policies, ttl=ttl)
            return response['auth']['client_token']
        except hvac.exceptions.VaultError as e:
            logging.error(f"Token creation failed: {str(e)}")
            return None
