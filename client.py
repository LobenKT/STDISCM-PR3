import socket

def send_range(start, end, server_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        s.sendall(f"{start},{end}".encode())
        result = s.recv(1024).decode()
    return result

def main():
    start, end = map(int, input("Enter start and end of range: ").split())
    server_address = ('localhost', 10000)  # Master server address
    primes = send_range(start, end, server_address)
    print("Primes:", primes)

if __name__ == "__main__":
    main()
