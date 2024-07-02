import socket

def send_range_and_receive_results(start, end, server_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to master server at {server_address}...")
        s.connect(server_address)
        s.sendall(f"{start},{end}".encode())

        # Keep receiving data until the connection is closed
        while True:
            result = s.recv(1024)
            if not result:
                break  # No more data, server has closed connection
            print("Received from server:")
            print(result.decode())

def main():
    start, end = map(int, input("Enter start and end of range: ").split())
    server_address = ('192.168.100.17', 10000)  # IP and port of the master server
    send_range_and_receive_results(start, end, server_address)

if __name__ == "__main__":
    print("Client is running...")
    main()
