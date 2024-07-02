import socket
from concurrent.futures import ThreadPoolExecutor
import time

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_primes_in_range(start, end):
    return [n for n in range(start, end + 1) if is_prime(n)]

def handle_request(start, end, thread_count):
    chunk_size = (end - start + 1) // thread_count
    ranges = [(start + i * chunk_size, start + (i + 1) * chunk_size - 1) for i in range(thread_count)]
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        result_lists = executor.map(lambda args: find_primes_in_range(*args), ranges)
    return [item for sublist in result_lists for item in sublist]  # Flatten the list of lists

def handle_client(conn, thread_count):
    range_data = conn.recv(1024).decode()
    start, end = map(int, range_data.split(','))
    print(f"Received range: {start} to {end}, calculating with {thread_count} threads...")
    start_time = time.time()
    primes = handle_request(start, end, thread_count)
    end_time = time.time()
    runtime = end_time - start_time
    conn.sendall(f"Found {len(primes)} primes in {runtime:.2f} seconds.".encode())
    conn.close()
    print(f"Task completed in {runtime:.2f} seconds.")

def main():
    thread_count = 8  # Example thread count, adjust as necessary for your experiments
    server_address = ('192.168.100.17', 10000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Master server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            handle_client(conn, thread_count)

if __name__ == "__main__":
    main()

# Uncomment below to restore the original distributed functionality
"""
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
"""
