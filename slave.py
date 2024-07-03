import socket
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np

def sieve_of_eratosthenes(limit):
    """ Use the Sieve of Eratosthenes to find all prime numbers up to 'limit'. """
    is_prime = np.ones(limit + 1, dtype=bool)
    p = 2
    while (p * p <= limit):
        if is_prime[p]:
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
        p += 1
    is_prime[0], is_prime[1] = False, False  # 0 and 1 are not prime numbers
    return is_prime

def segmented_sieve(start, end, base_primes):
    """ Apply a segmented sieve of Eratosthenes to find all primes in a specific range. """
    size = end - start + 1
    is_prime = np.ones(size, dtype=bool)
    for p in base_primes:
        if p * p > end:
            break
        start_index = max(p * p, (start + p - 1) // p * p) - start
        for j in range(start_index, size, p):
            is_prime[j] = False
    if start == 1:
        is_prime[0] = False
    return [start + i for i in range(size) if is_prime[i]]

def handle_request(start, end, thread_count, base_primes):
    """ Handle the prime calculation request for a specified range and thread count. """
    primes = segmented_sieve(start, end, base_primes)
    return primes

def main():
    server_address = ('192.168.100.17', 10000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Slave server is running and listening at {server_address}...")

        while True:
            conn, addr = s.accept()
            print(f"Connected to master at {addr}")
            try:
                while True:  # Keep the connection open
                    data = conn.recv(1024).decode()
                    if not data:
                        print("No more data received. Closing connection.")
                        break  # Exit the loop to close the connection
                    start, end, thread_count = map(int, data.split(','))
                    print(f"Received range: {start} to {end}, with thread count {thread_count}.")

                    base_primes = sieve_of_eratosthenes(int(end**0.5) + 1)
                    primes = handle_request(start, end, thread_count, base_primes)
                    prime_count = len(primes)
                    response = str(prime_count)

                    print(f"Found {prime_count} primes in range {start} to {end}.")
                    print(f"Sending response to master: {response}")
                    conn.sendall(response.encode())

            except socket.error as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"Unhandled error: {e}")
            finally:
                conn.close()
                print("Connection closed.")

if __name__ == "__main__":
    main()
