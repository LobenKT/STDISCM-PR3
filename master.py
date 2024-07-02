import socket
from threading import Thread

def handle_client(conn, slave_address):
    print("Received connection from client.")
    range_data = conn.recv(1024).decode()
    start, end = map(int, range_data.split(','))
    print(f"Received range: {start} to {end} from client, forwarding to slave...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(slave_address)
        s.sendall(range_data.encode())
        result = s.recv(1024).decode()
    conn.sendall(result.encode())
    conn.close()
    print("Result sent back to client.")

def main():
    slave_address = ('localhost', 10001)  # Change to actual slave server IP and port
    server_address = ('', 10000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Master server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            Thread(target=handle_client, args=(conn, slave_address)).start()

if __name__ == "__main__":
    main()
