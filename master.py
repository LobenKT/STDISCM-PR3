import socket
from threading import Thread

def handle_client(conn, slave_address):
    range_data = conn.recv(1024).decode()
    start, end = map(int, range_data.split(','))
    # Assuming one slave for simplicity, in practice, divide range and manage multiple slaves
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(slave_address)
        s.sendall(range_data.encode())
        result = s.recv(1024).decode()
    conn.sendall(result.encode())
    conn.close()

def main():
    slave_address = ('localhost', 10001)  # Address of slave server
    server_address = ('', 10000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        while True:
            conn, _ = s.accept()
            Thread(target=handle_client, args=(conn, slave_address)).start()

if __name__ == "__main__":
    main()
