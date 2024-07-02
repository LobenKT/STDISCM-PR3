import socket
from concurrent.futures import ThreadPoolExecutor
import time

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
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

def main():
    thread_counts = [2**i for i in range(0, 11)]  # Generates [1, 2, 4, ..., 1024]
    server_address = ('192.168.100.17', 10000)
    slave_address = ('192.168.100.4', 10001)  # Address of the slave server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Master server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            range_data = conn.recv(1024).decode()
            start, end = map(int, range_data.split(','))

            for thread_count in thread_counts:
                mid_point = start + (end - start) // 2
                # Master handles the first half
                master_primes = handle_request(start, mid_point, thread_count)
                # Slave handles the second half
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as slave_socket:
                    slave_socket.connect(slave_address)
                    slave_socket.sendall(f"{mid_point+1},{end},{thread_count}".encode())
                    slave_result = slave_socket.recv(2048).decode()
                
                # Combine results and send back to client
                total_primes = len(master_primes) + int(slave_result.split()[-2])
                response = f"{thread_count} threads: Found {total_primes} primes."
                conn.sendall(response.encode())
                print(response)

            conn.close()

if __name__ == "__main__":
    main()
