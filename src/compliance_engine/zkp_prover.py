# orbital-agent/src/compliance_engine/zkp_prover.py
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import os

logger = logging.getLogger(__name__)

class ZKPProtocolError(Exception):
    """Base exception for ZKP protocol failures"""

class ZKPProver:
    def __init__(self, curve=ec.SECP256R1()):
        self.curve = curve
        self.private_key = ec.generate_private_key(curve, default_backend())
        self.public_key = self.private_key.public_key()
        self._nonce = None

    def generate_proof(self, witness: bytes, context: bytes = b'') -> bytes:
        """
        Generate Zero-Knowledge Proof using Schnorr protocol variant
        Returns proof as concatenated R | s
        """
        if not witness:
            raise ValueError("Invalid witness input")

        # Commitment phase
        k = self._generate_secure_nonce()
        R = k.public_key().public_numbers().public_key(default_backend())
        
        # Challenge construction
        challenge = self._compute_challenge(
            public_point=R.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.CompressedPoint
            ),
            witness=witness,
            context=context
        )
        
        # Response generation
        s = self._compute_response(k, challenge)
        
        proof = R.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        ) + s.to_bytes((s.bit_length() + 7) // 8, 'big')
        
        logger.debug("Generated ZKP for witness length: %d", len(witness))
        return proof

    def verify_proof(self, proof: bytes, witness: bytes, context: bytes = b'') -> bool:
        """Verify ZKP against public parameters and witness"""
        if len(proof) < 33:
            raise ZKPProtocolError("Invalid proof length")
        
        try:
            R_bytes = proof[:33]
            s_bytes = proof[33:]
            
            R = ec.EllipticCurvePublicKey.from_encoded_point(
                curve=self.curve,
                data=R_bytes
            )
            s = int.from_bytes(s_bytes, 'big')
            
            challenge = self._compute_challenge(R_bytes, witness, context)
            generator = self.curve.generator
            
            lhs = generator * s
            rhs = R.public_numbers().public_key(default_backend()) + \
                self.public_key.public_numbers().public_key(default_backend()) * challenge
            
            return lhs.public_numbers() == rhs.public_numbers()
        except (ValueError, InvalidSignature) as e:
            logger.warning("Proof verification failed: %s", str(e))
            return False

    def serialize_public_key(self) -> bytes:
        """Export public key in PEM format"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @classmethod
    def deserialize_public_key(cls, pem_data: bytes, curve=ec.SECP256R1()):
        """Load public key from PEM data"""
        public_key = serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )
        instance = cls(curve)
        instance.public_key = public_key
        return instance

    def _generate_secure_nonce(self):
        """Cryptographically secure nonce generation"""
        return ec.generate_private_key(self.curve, default_backend())

    def _compute_challenge(self, public_point: bytes, witness: bytes, context: bytes) -> int:
        """Compute Fiat-Shamir challenge"""
        hasher = hashes.Hash(hashes.SHA256(), default_backend())
        hasher.update(public_point)
        hasher.update(witness)
        hasher.update(context)
        return int.from_bytes(hasher.finalize(), 'big') % self.curve.order

    def _compute_response(self, k: ec.EllipticCurvePrivateKey, challenge: int) -> int:
        """Calculate response value s = k + c * x mod n"""
        x = self.private_key.private_numbers().private_value
        k_val = k.private_numbers().private_value
        return (k_val + challenge * x) % self.curve.order

class ZKPVerifier:
    def __init__(self, public_key: ec.EllipticCurvePublicKey, curve=ec.SECP256R1()):
        self.public_key = public_key
        self.curve = curve

    def verify(self, proof: bytes, witness: bytes, context: bytes = b'') -> bool:
        """Verify proof using stored public key"""
        prover = ZKPProver(self.curve)
        prover.public_key = self.public_key
        return prover.verify_proof(proof, witness, context)
