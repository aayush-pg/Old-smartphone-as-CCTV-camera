#!/usr/bin/env python3
"""
Generate self-signed SSL certificate for HTTPS
"""
import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import ipaddress

def generate_self_signed_cert():
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Get local IP address and hostname
    import socket
    hostname = socket.gethostname()
    
    # Try multiple methods to get IP addresses
    local_ips = []
    try:
        # Method 1: Connect to external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        local_ips.append(primary_ip)
        s.close()
    except:
        primary_ip = "127.0.0.1"
    
    try:
        # Method 2: Get all host IPs
        _, _, ip_list = socket.gethostbyname_ex(hostname)
        for ip in ip_list:
            if ip not in local_ips and not ip.startswith("127."):
                local_ips.append(ip)
    except:
        pass
    
    # Ensure localhost is included
    if "127.0.0.1" not in local_ips:
        local_ips.append("127.0.0.1")
    
    print(f"Generating certificate for IPs: {local_ips}")
    print(f"Hostname: {hostname}")

    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WebWatch"),
        x509.NameAttribute(NameOID.COMMON_NAME, primary_ip),
    ])

    # Build Subject Alternative Names
    san_list = [
        x509.DNSName("localhost"),
        x509.DNSName(hostname),
    ]
    
    # Add all IP addresses
    for ip in local_ips:
        try:
            san_list.append(x509.IPAddress(ipaddress.ip_address(ip)))
        except:
            pass  # Skip invalid IPs

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.UTC)
    ).not_valid_after(
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Write certificate and key to files
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open("key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print("✅ SSL Certificate generated:")
    print("   - cert.pem (certificate)")
    print("   - key.pem (private key)")
    print(f"   - Valid for IPs: {', '.join(local_ips)}")
    print(f"   - Valid for hostnames: localhost, {hostname}")

if __name__ == "__main__":
    generate_self_signed_cert()