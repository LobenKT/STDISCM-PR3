import socket
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import time

def sieve_of_eratosthenes(limit):
    """ Use the Sieve of Eratosthenes to find all prime numbers up to 'limit'. """
    is_prime = np.ones(limit + 1, dtype=np.bool_)
    p = 2
    while (p * p <= limit):
        if is_prime[p]:
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
        p += 1
    is_prime[0], is_prime[1] = False, False  # 0 and 1 are not prime numbers
    return np.nonzero(is_prime)[0]

def segmented_sieve(start, end, base_primes):
    """ Apply a segmented sieve of Eratosthenes to find all primes in a specific range. """
    if start > end:
        return []  # Handle case where the range is invalid
    size = end - start + 1
    is_prime = np.ones(size, dtype=np.bool_)
    for p in base_primes:
        if p * p > end:
            break
        start_index = max(p * p, (start + p - 1) // p * p) - start
        for j in range(start_index, size, p):
            is_prime[j] = False
    if start == 1:
        is_prime[0] = False
    return [start + i for i in range(size) if is_prime[i]]

def handle_request(start, end):
    """ Handle the prime calculation request for a specified range. """
    sqrt_limit = int(end**0.5) + 1
    base_primes = sieve_of_eratosthenes(sqrt_limit)
    return segmented_sieve(start, end, base_primes)

def main():
    server_address = ('192.168.100.6', 10002)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(server_address)
        server_socket.listen()
        print(f"Slave server is running and listening at {server_address}...")

        while True:
            conn, addr = server_socket.accept()
            print(f"Connected to master at {addr}")
            try:
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        print("No more data received. Connection may be closed.")
                        break
                    start, end = map(int, data.split(','))
                    print(f"Received range: {start} to {end}.")
                    primes = handle_request(start, end)
                    prime_count = len(primes)
                    response = str(prime_count)
                    conn.sendall(response.encode())
                    print(f"Sent {prime_count} primes count to master.")
            except socket.error as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"Unhandled error: {e}")
            finally:
                conn.close()
                print("Connection with master closed.")

if __name__ == "__main__":
    main()
