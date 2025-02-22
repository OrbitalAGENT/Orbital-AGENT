# orbital-agent/src/compliance_engine/homomorphic_enc.py
import logging
import numpy as np
from Pyfhel import Pyfhel, PyCtxt, PyPtxt
from typing import Union, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class HomomorphicEncryptionError(Exception):
    """Base exception for homomorphic operations"""

class HomomorphicEncryption:
    def __init__(self, scheme: str = 'BFV', security_level: int = 128):
        self.he = Pyfhel()
        self.scheme = scheme.upper()
        self.security_level = security_level
        self._default_params = self._get_scheme_parameters()

    def generate_keys(self, params: Optional[dict] = None) -> None:
        """Generate cryptographic context and keys"""
        try:
            if not params:
                params = self._default_params

            if self.scheme == 'BFV':
                self.he.contextGen(**params)
            elif self.scheme == 'CKKS':
                self.he.contextGen(
                    scheme=self.scheme,
                    n=params['n'],
                    scale=params['scale'],
                    qi_sizes=params['qi_sizes']
                )
            else:
                raise ValueError("Unsupported scheme")

            self.he.keyGen()
            self.he.relinKeyGen()
            self.he.rotateKeyGen()
            logger.info(f"Generated {self.scheme} keys with {self.security_level}-bit security")
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise HomomorphicEncryptionError("Key generation error") from e

    def encrypt(self, data: Union[int, float, np.ndarray]) -> PyCtxt:
        """Encrypt data using current context"""
        self._validate_context()
        try:
            if isinstance(data, (int, float)):
                return self.he.encryptFrac(data) if self.scheme == 'CKKS' else self.he.encryptInt(int(data))
            elif isinstance(data, np.ndarray):
                return self.he.encryptMatrix(data)
            raise TypeError("Unsupported data type for encryption")
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise HomomorphicEncryptionError("Encryption error") from e

    def decrypt(self, ciphertext: PyCtxt) -> Union[int, float, np.ndarray]:
        """Decrypt ciphertext using current context"""
        self._validate_context()
        try:
            if self.scheme == 'CKKS':
                return self.he.decryptFrac(ciphertext)
            return self.he.decryptInt(ciphertext)
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise HomomorphicEncryptionError("Decryption error") from e

    def add(self, c1: PyCtxt, c2: Union[PyCtxt, int, float]) -> PyCtxt:
        """Homomorphic addition"""
        return c1 + c2

    def multiply(self, c1: PyCtxt, c2: Union[PyCtxt, int, float]) -> PyCtxt:
        """Homomorphic multiplication"""
        result = c1 * c2
        if isinstance(c2, PyCtxt):
            self.he.relinearize(result)
        return result

    def save_context(self, path: str) -> None:
        """Save cryptographic context and keys"""
        context = {
            'scheme': self.scheme,
            'security_level': self.security_level,
            'params': self._get_current_parameters()
        }
        self.he.saveContext(Path(path) / "context")
        with open(Path(path) / "config.json", 'w') as f:
            json.dump(context, f)
        logger.info(f"Saved HE context to {path}")

    def load_context(self, path: str) -> None:
        """Load cryptographic context and keys"""
        with open(Path(path) / "config.json", 'r') as f:
            context = json.load(f)
        self.scheme = context['scheme']
        self.security_level = context['security_level']
        self._default_params = context['params']
        self.he.restoreContext(Path(path) / "context")
        logger.info(f"Loaded HE context from {path}")

    def _get_scheme_parameters(self) -> dict:
        """Get default parameters based on security level"""
        params_map = {
            128: {
                'BFV': {'n': 4096, 't': 1032193, 'sec': 128},
                'CKKS': {'n': 8192, 'scale': 2**30, 'qi_sizes': [60, 40, 40, 60]}
            },
            256: {
                'BFV': {'n': 8192, 't': 2064385, 'sec': 256},
                'CKKS': {'n': 16384, 'scale': 2**40, 'qi_sizes': [60, 50, 50, 50, 60]}
            }
        }
        return params_map[self.security_level][self.scheme]

    def _get_current_parameters(self) -> dict:
        """Retrieve current context parameters"""
        if self.scheme == 'BFV':
            return {
                'n': self.he.n,
                't': self.he.t,
                'sec': self.he.sec
            }
        return {
            'n': self.he.n,
            'scale': self.he.scale,
            'qi_sizes': self.he.qi_sizes
        }

    def _validate_context(self) -> None:
        """Check if valid context exists"""
        if not self.he.context.is_initialized():
            raise HomomorphicEncryptionError("No cryptographic context initialized")

class EncryptedDataProcessor:
    def __init__(self, he: HomomorphicEncryption):
        self.he = he
        self.operations_log = []

    def process_encrypted_data(self, ciphertexts: list, operations: list) -> PyCtxt:
        """Execute sequence of operations on encrypted data"""
        result = ciphertexts[0]
        for op in operations:
            if op['type'] == 'add':
                result = self._execute_add(result, op)
            elif op['type'] == 'multiply':
                result = self._execute_multiply(result, op)
            self._log_operation(op)
        return result

    def _execute_add(self, ctxt: PyCtxt, operation: dict) -> PyCtxt:
        """Perform homomorphic addition"""
        operand = operation.get('operand')
        if isinstance(operand, (int, float)):
            return self.he.add(ctxt, operand)
        return self.he.add(ctxt, operand)

    def _execute_multiply(self, ctxt: PyCtxt, operation: dict) -> PyCtxt:
        """Perform homomorphic multiplication"""
        operand = operation.get('operand')
        if isinstance(operand, (int, float)):
            return self.he.multiply(ctxt, operand)
        return self.he.multiply(ctxt, operand)

    def _log_operation(self, operation: dict) -> None:
        """Record operation metadata"""
        self.operations_log.append({
            'operation': operation['type'],
            'timestamp': time.time(),
            'parameters': operation.get('params', {})
        })
