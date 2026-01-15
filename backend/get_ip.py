#!/usr/bin/env python3
"""
Utility script to get the current local IP address
"""
import socket
import sys

def get_local_ip():
    """Get the local IP address dynamically"""
    try:
        # Method 1: Connect to a remote server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Method 1 failed: {e}", file=sys.stderr)
        
        try:
            # Method 2: Get hostname and resolve it
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip.startswith("127."):
                raise Exception("Got localhost IP")
            return local_ip
        except Exception as e2:
            print(f"Method 2 failed: {e2}", file=sys.stderr)
            return "localhost"

def get_all_ips():
    """Get all available IP addresses"""
    hostname = socket.gethostname()
    try:
        # Get all IP addresses associated with the hostname
        ip_list = socket.gethostbyname_ex(hostname)[2]
        # Filter out localhost addresses
        ip_list = [ip for ip in ip_list if not ip.startswith("127.")]
        return ip_list
    except Exception as e:
        print(f"Error getting all IPs: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    print("Current Local IP Address:")
    print(f"Primary IP: {get_local_ip()}")
    
    all_ips = get_all_ips()
    if all_ips:
        print("\nAll available IP addresses:")
        for i, ip in enumerate(all_ips, 1):
            print(f"  {i}. {ip}")
    
    print(f"\nBackend will be available at: https://{get_local_ip()}:5000")
    print(f"Frontend will be available at: https://{get_local_ip()}:3000")