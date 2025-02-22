// orbital-agent/src/security/crypto.rs
use ring::{aead, hkdf, rand::SystemRandom};
use std::error::Error;

pub struct CryptoEngine {
    key: [u8; 32],
    rng: SystemRandom,
}

impl CryptoEngine {
    pub fn new(key: [u8; 32]) -> Self {
        CryptoEngine {
            key,
            rng: SystemRandom::new(),
        }
    }

    pub fn encrypt(&self, data: &[u8]) -> Result<Vec<u8>, Box<dyn Error>> {
        let nonce = self.generate_nonce()?;
        let sealing_key = self.derive_sealing_key(&nonce)?;
        
        let mut ciphertext = data.to_vec();
        sealing_key.seal_in_place_append_tag(&mut ciphertext)
            .map_err(|e| e.to_string())?;
        
        Ok([nonce.as_ref(), &ciphertext].concat())
    }

    fn generate_nonce(&self) -> Result<aead::Nonce, Box<dyn Error>> {
        let mut nonce = [0u8; 12];
        self.rng.fill(&mut nonce)?;
        Ok(aead::Nonce::assume_unique_for_key(nonce))
    }

    fn derive_sealing_key(&self, nonce: &aead::Nonce) -> Result<aead::SealingKey, Box<dyn Error>> {
        let salt = hkdf::Salt::new(hkdf::HKDF_SHA256, &self.key);
        let prk = salt.extract(nonce.as_ref());
        Ok(prk.expand(&[b"encryption"], aead::AES_256_GCM)?)
    }
}
