import socket

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def main():
    server_address = ('', 10001)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Slave server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            print("Connection received from master server.")
            range_data = conn.recv(1024).decode()
            start, end = map(int, range_data.split(','))
            primes = [str(i) for i in range(start, end + 1) if is_prime(i)]
            conn.sendall(','.join(primes).encode())
            conn.close()
            print(f"Primes calculated for range {start}-{end} and sent back.")

if __name__ == "__main__":
    main()
