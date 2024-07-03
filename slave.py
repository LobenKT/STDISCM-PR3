import socket
from concurrent.futures import ThreadPoolExecutor
import time

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0 and n!=2:
            return False
    return True

def find_primes_in_range(start, end):
    return [n for n in range(start, end + 1) if is_prime(n)]

def handle_request(start, end, thread_count):
    total_range = end - start + 1
    chunk_size = max(1, total_range // thread_count)  # Ensure at least one number per thread
    ranges = [(start + i * chunk_size, min(end, start + (i + 1) * chunk_size - 1)) for i in range(thread_count)]
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        result_lists = executor.map(lambda args: find_primes_in_range(*args), ranges)
    return [item for sublist in result_lists for item in sublist]

def main():
    server_address = ('192.168.100.17', 10000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Slave server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            conn.settimeout(60)  # Set timeout for the connection to 60 seconds
            try:
                data = conn.recv(1024).decode()
                if data:
                    start, end, thread_count = map(int, data.split(','))
                    print(f"Received data: '{data}'")
                    print(f"Received range: {start} to {end} from master with {thread_count} threads.")
                    primes = handle_request(start, end, thread_count)
                    prime_count = len(primes)
                    print(f"Found {prime_count} primes in range {start} to {end}.")
                    conn.sendall(str(prime_count).encode())
                else:
                    print("No data received or data is incomplete.")
            except socket.timeout:
                print("No further data received. Connection timed out.")
            finally:
                conn.close()
                print("Connection closed.")

if __name__ == "__main__":
    main()
