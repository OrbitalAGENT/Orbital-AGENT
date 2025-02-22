# Base image with TEE support
FROM gramineproject/ubuntu:20.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    python3.8 \
    openssl \
    intel-sgx-ssl \
    az-dcap-client

# Configure Python environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Deploy Hyperledger components
COPY scripts/deploy_hyperledger.sh .
RUN ./deploy_hyperledger.sh

# Expose core ports
EXPOSE 5000  # API Gateway
EXPOSE 8787  # TEE Worker
EXPOSE 7054  # Hyperledger CA

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
