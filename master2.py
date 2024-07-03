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
    chunk_size = total_range // thread_count
    ranges = [(start + i * chunk_size, (start + (i + 1) * chunk_size - 1) if i < thread_count - 1 else end) for i in range(thread_count)]
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        result_lists = executor.map(lambda args: find_primes_in_range(*args), ranges)
    return [item for sublist in result_lists for item in sublist]

def attempt_slave_connection(slave_address):
    try:
        slave_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        slave_socket.connect(slave_address)
        print("Connected to slave server successfully.")
        return slave_socket, True
    except socket.error as e:
        print(f"Failed to connect to slave server: {e}")
        return None, False

def handle_client(conn, slave_socket, slave_active, thread_counts):
    try:
        range_data = conn.recv(1024).decode()
        start, end = map(int, range_data.split(','))
        for thread_count in thread_counts:
            print(f"Received range: {start} to {end}, calculating with {thread_count} threads...")
            start_time = time.time()
            if slave_active:
                mid_point = start + (end - start) // 2
                master_primes = handle_request(start, mid_point, thread_count)
                slave_socket.sendall(f"{mid_point + 1},{end},{thread_count}".encode())
                try:
                    response = slave_socket.recv(1024).decode().strip()
                    if response.isdigit():
                        total_primes = len(master_primes) + int(response)
                        print(f"Received {response} primes from slave.")
                    else:
                        print(f"Invalid or no data received from slave, received: '{response}'")
                        total_primes = len(master_primes)
                except socket.error as e:
                    print(f"Failed to receive data from slave: {e}")
                    total_primes = len(master_primes)
            else:
                total_primes = len(handle_request(start, end, thread_count))
            runtime_ms = (time.time() - start_time) * 1000
            response = f"{thread_count} threads: Found {total_primes} primes in {runtime_ms:.2f} ms."
            conn.sendall(response.encode())
            print(response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def main():
    thread_counts = [2**i for i in range(0, 11)]
    server_address = ('192.168.100.4', 10001)
    slave_address = ('192.168.100.17', 10000)
    slave_socket, slave_active = attempt_slave_connection(slave_address)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Master server is running and listening at {server_address}...")
        while True:
            try:
                conn, _ = s.accept()
                handle_client(conn, slave_socket, slave_active, thread_counts)
            except Exception as e:
                print(f"Master server operational error: {e}")
            # Re-attempt to connect to slave every 30 seconds if not connected
            if not slave_active:
                time.sleep(30)
                slave_socket, slave_active = attempt_slave_connection(slave_address)

if __name__ == "__main__":
    main()
