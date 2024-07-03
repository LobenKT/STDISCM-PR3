import socket
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import time

def sieve_of_eratosthenes(limit):
    """ Compute all primes up to 'limit' using the Sieve of Eratosthenes. """
    is_prime = np.ones(limit + 1, dtype=bool)
    for p in range(2, int(limit**0.5) + 1):
        if is_prime[p]:
            is_prime[p*p:limit+1:p] = False
    is_prime[0:2] = False  # 0 and 1 are not prime numbers
    return np.nonzero(is_prime)[0]

def segmented_sieve(start, end, base_primes):
    """ Use a segmented sieve to find all primes in the range [start, end]. """
    if start > end:
        return []  # Return an empty list if the range is invalid.
    size = end - start + 1
    is_prime = np.ones(size, dtype=bool)
    for p in base_primes:
        if p * p > end:
            break
        # Start index is adjusted for the first multiple of p within the range.
        start_index = max(p*p, ((start + p - 1) // p) * p) - start
        is_prime[start_index::p] = False
    if start == 1:
        is_prime[0] = False  # Ensure '1' is not considered a prime.
    primes = np.nonzero(is_prime)[0] + start
    return primes.tolist()

def handle_request(start, end):
    """ Handle the prime calculation for a specified range. """
    sqrt_limit = int(end**0.5) + 1
    base_primes = sieve_of_eratosthenes(sqrt_limit)
    primes = segmented_sieve(start, end, base_primes)
    return primes

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
                data = conn.recv(1024).decode()
                if data:
                    start, end = map(int, data.split(','))
                    print(f"Received range: {start} to {end}. Processing...")
                    primes = handle_request(start, end)
                    prime_count = len(primes)
                    print(f"Found {prime_count} primes in the range {start} to {end}.")
                    conn.sendall(str(prime_count).encode())
                else:
                    print("No data received or data is incomplete.")
            except socket.error as e:
                print(f"Socket error: {e}")
            except ValueError as e:
                print(f"Value error: {e} -- possibly incorrect data format.")
            except Exception as e:
                print(f"Unhandled error: {e}")
            finally:
                conn.close()
                print("Connection closed with master.")

if __name__ == "__main__":
    main()
