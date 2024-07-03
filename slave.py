import socket
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np

def sieve_of_eratosthenes(limit):
    is_prime = np.ones(limit + 1, dtype=bool)
    p = 2
    while (p * p <= limit):
        if is_prime[p]:
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
        p += 1
    is_prime[0], is_prime[1] = False, False
    return is_prime

def segmented_sieve(start, end, base_primes):
    size = end - start + 1
    is_prime = np.ones(size, dtype=bool)
    for p in base_primes:
        if p * p > end:
            break
        # Find the minimum number in the [start, end] range that is a multiple of p
        start_index = max(p * p, (start + p - 1) // p * p) - start
        for j in range(start_index, size, p):
            is_prime[j] = False
    if start == 1:
        is_prime[0] = False  # 1 is not a prime number
    return [start + i for i in range(size) if is_prime[i]]

def handle_request(start, end, thread_count):
    # Assume base primes are precomputed up to the square root of the end of the range
    sqrt_limit = int(end**0.5) + 1
    base_primes = sieve_of_eratosthenes(sqrt_limit)
    return segmented_sieve(start, end, base_primes)

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
                    start, end = map(int, data.split(','))
                    print(f"Received range: {start} to {end}.")
                    primes = handle_request(start, end, 1)  # Thread count is 1 for simplicity
                    prime_count = len(primes)
                    print(f"Found {prime_count} primes in range {start} to {end}.")
                    conn.sendall(str(prime_count).encode())
                else:
                    print("No data received or data is incomplete.")
            except socket.timeout:
                print("Connection timed out, no further data received.")
            except Exception as e:
                print(f"Error during connection: {e}")
            finally:
                conn.close()
                print("Connection closed.")

if __name__ == "__main__":
    main()
