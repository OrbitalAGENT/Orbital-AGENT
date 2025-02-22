from zkp import Groth16
from hashlib import sha256
import json

class ComplianceProver:
    def __init__(self, circuit_file: str):
        self.prover = Groth16(circuit_file)
        
    def generate_audit_proof(self, transaction: dict) -> dict:
        """Generate ZKP for GDPR/HIPAA compliance"""
        # Convert transaction to circuit inputs
        inputs = self._hash_transaction(transaction)
        proof = self.prover.prove(inputs)
        return {
            "proof": proof.serialize(),
            "public_signals": inputs['public'],
            "timestamp": transaction['timestamp']
        }

    def _hash_transaction(self, tx: dict) -> dict:
        """Convert transaction data to circuit-compatible format"""
        private_hash = sha256(json.dumps(tx['private']).encode()).hexdigest()
        public_hash = sha256(json.dumps(tx['public']).encode()).hexdigest()
        return {
            "private": [int(private_hash[i:i+8], 16) for i in range(0, 64, 8)],
            "public": [int(public_hash[i:i+8], 16) for i in range(0, 64, 8)]
        }

class AuditVerifier:
    def verify_proof(self, proof_data: dict) -> bool:
        verifier = Groth16("circuits/compliance_circuit.zkey")
        return verifier.verify(
            proof_data['proof'],
            proof_data['public_signals']
        )
