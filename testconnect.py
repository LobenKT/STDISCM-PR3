import socket

def test_connection(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=10) as sock:
            print(f"Successfully connected to {ip} on port {port}")
    except socket.error as e:
        print(f"Failed to connect to {ip} on port {port}: {e}")

test_connection('192.168.100.17', 10000)  # Test slave
test_connection('192.168.100.6', 10001)   # Test master
