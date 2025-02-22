// orbital-agent/src/security/zero_trust.rs
use std::net::SocketAddr;
use tokio::net::TcpStream;
use crate::auth::JwtValidator;

pub struct ZeroTrustProxy {
    jwt_validator: JwtValidator,
    upstream_addr: SocketAddr,
}

impl ZeroTrustProxy {
    pub fn new(validator: JwtValidator, upstream: SocketAddr) -> Self {
        Self { jwt_validator, upstream_addr: upstream }
    }

    pub async fn handle_connection(&self, mut inbound: TcpStream) -> Result<(), Box<dyn std::error::Error>> {
        let (mut client_reader, mut client_writer) = inbound.split();
        let mut upstream = TcpStream::connect(self.upstream_addr).await?;
        
        // Mutual TLS verification
        let peer_cert = inbound.peer_certificate()?;
        self.jwt_validator.validate(peer_cert)?;
        
        // Secure tunneling
        tokio::io::copy_bidirectional(&mut client_reader, &mut upstream).await?;
        Ok(())
    }
}
