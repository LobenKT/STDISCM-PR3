import socket

def send_range(start, end, server_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to master server at {server_address}...")
        s.connect(server_address)
        s.sendall(f"{start},{end}".encode())
        result = s.recv(1024).decode()
    return result

def main():
    start, end = map(int, input("Enter start and end of range: ").split())
    server_address = ('192.168.100.17', 10000)  # IP and port of the master server
    primes = send_range(start, end, server_address)
    print("Primes received from server:")
    print(primes)

if __name__ == "__main__":
    print("Client is running...")
    main()
