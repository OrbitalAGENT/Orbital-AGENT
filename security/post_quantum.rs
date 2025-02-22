// orbital-agent/src/security/post_quantum.rs
use pqcrypto::kem::kyber1024::*;
use pqcrypto::prelude::*;

pub struct KyberWrapper {
    public_key: PublicKey,
    secret_key: SecretKey,
}

impl KyberWrapper {
    pub fn new() -> Self {
        let (pk, sk) = keypair();
        KyberWrapper {
            public_key: pk,
            secret_key: sk,
        }
    }

    pub fn encrypt(&self) -> (Ciphertext, SharedSecret) {
        encapsulate(&self.public_key)
    }

    pub fn decrypt(&self, ct: &Ciphertext) -> SharedSecret {
        decapsulate(ct, &self.secret_key)
    }
}
