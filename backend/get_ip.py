import socket
import subprocess
import re

def get_local_ip():
    """Get the local IP address dynamically"""
    try:
        # Method 1: Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Method 2: Use ipconfig on Windows
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            # Look for IPv4 address in Wi-Fi adapter
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'Wireless LAN adapter Wi-Fi:' in line or 'Wi-Fi:' in line:
                    # Look for IPv4 in next few lines
                    for j in range(i, min(i+10, len(lines))):
                        if 'IPv4 Address' in lines[j]:
                            match = re.search(r'(\d+\.\d+\.\d+\.\d+)', lines[j])
                            if match:
                                return match.group(1)
        except:
            pass
    
    # Fallback
    return '127.0.0.1'

if __name__ == "__main__":
    print(get_local_ip())