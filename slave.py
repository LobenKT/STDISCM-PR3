import socket
from concurrent.futures import ThreadPoolExecutor

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_primes_in_range(start, end):
    return [n for n in range(start, end + 1) if is_prime(n)]

def handle_task(start, end, thread_count):
    chunk_size = (end - start + 1) // thread_count
    ranges = [(start + i * chunk_size, start + (i + 1) * chunk_size - 1) for i in range(thread_count)]
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        result_lists = executor.map(lambda args: find_primes_in_range(*args), ranges)
    return [item for sublist in result_lists for item in sublist]  # Flatten the list of lists

def main():
    server_address = ('192.168.100.4', 10001)  # Adjust the IP address as necessary
    thread_count = 8  # Adjust the number of threads as necessary
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Slave server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            print("Connection received from master server.")
            range_data = conn.recv(1024).decode()
            start, end = map(int, range_data.split(','))
            primes = handle_task(start, end, thread_count)
            conn.sendall(','.join(map(str, primes)).encode())
            conn.close()
            print(f"Processed range {start}-{end} and sent back.")

if __name__ == "__main__":
    main()
