import socket
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_primes_in_range(start, end):
    return [n for n in range(start, end + 1) if is_prime(n)]

def sieve_of_eratosthenes(limit):
    is_prime = np.ones(limit + 1, dtype=bool)
    p = 2
    while (p * p <= limit):
        if is_prime[p]:
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
        p += 1
    is_prime[0], is_prime[1] = False, False  # 0 and 1 are not prime numbers
    return is_prime

def handle_request(start, end, thread_count, small_primes):
    total_range = end - start + 1
    chunk_size = total_range // thread_count
    ranges = [(start + i * chunk_size, (start + (i + 1) * chunk_size - 1) if i < thread_count - 1 else end) for i in range(thread_count)]
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        args = [(r[0], r[1], small_primes) for r in ranges]
        result_lists = executor.map(lambda x: find_primes_in_range(x[0], x[1]), args)
    return [item for sublist in result_lists for item in sublist]

def attempt_slave_connection(slave_address):
    slave_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        slave_socket.connect(slave_address)
        print("Connected to slave server successfully.")
        return slave_socket, True
    except socket.error as e:
        print(f"Failed to connect to slave server: {e}")
        return None, False
    finally:
        # It's a good practice to set a timeout for socket operations to avoid hanging indefinitely
        slave_socket.settimeout(10)


def handle_client(conn, slave_socket, slave_active, thread_counts, small_primes):
    try:
        range_data = conn.recv(1024).decode()
        start, end = map(int, range_data.split(','))
        print(f"Client has requested primes from {start} to {end}.")
        for thread_count in thread_counts:
            print(f"Calculating with {thread_count} threads...")
            start_time = time.time()
            if slave_active:
                mid_point = start + (end - start) // 2
                master_primes = handle_request(start, mid_point, thread_count, small_primes)
                slave_socket.sendall(f"{mid_point + 1},{end},{thread_count}".encode())
                response = slave_socket.recv(1024).decode().strip()
                total_primes = len(master_primes) + int(response) if response.isdigit() else len(master_primes)
                print(f"Received {response} primes from slave.")
            else:
                total_primes = len(handle_request(start, end, thread_count, small_primes))
            runtime_ms = (time.time() - start_time) * 1000
            response = f"{thread_count} threads: Found {total_primes} primes in {runtime_ms:.2f} ms."
            conn.sendall(response.encode())
            print(response)
    except Exception as e:
        print(f"Error handling client request: {e}")
    finally:
        conn.close()

def main():
    thread_counts = [2**i for i in range(0, 11)]
    server_address = ('192.168.100.4', 10001)
    slave_address = ('192.168.100.17', 10000)
    small_primes = sieve_of_eratosthenes(int(10**4))  # Precompute small primes for efficiency

    slave_socket, slave_active = attempt_slave_connection(slave_address)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Master server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            handle_client(conn, slave_socket, slave_active, thread_counts, small_primes)

if __name__ == "__main__":
    main()
