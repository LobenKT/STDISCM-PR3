import socket
from concurrent.futures import ThreadPoolExecutor

def find_primes_in_range(start, end):
    """A placeholder function that should be implemented to find primes in a range."""
    primes = []
    for num in range(start, end + 1):
        if num > 1:
            for i in range(2, num):
                if (num % i) == 0:
                    break
            else:
                primes.append(num)
    return primes

def handle_request(start, end, thread_count):
    total_range = end - start + 1
    chunk_size = max(1, total_range // thread_count)  # Ensure at least one number per thread
    ranges = [(start + i * chunk_size, min(end, start + (i + 1) * chunk_size - 1)) for i in range(thread_count)]
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        result_lists = executor.map(lambda args: find_primes_in_range(*args), ranges)
    return [item for sublist in result_lists for item in sublist]

def main():
    server_address = ('192.168.254.156', 10000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(server_address)
        s.listen()
        print(f"Slave server is running and listening at {server_address}...")
        while True:
            conn, _ = s.accept()
            conn.settimeout(60)  # Set timeout for the connection to 60 seconds
            try:
                while True:
                    data = conn.recv(1024).decode().strip()
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
                        break
            except socket.timeout:
                print("No further data received. Connection timed out.")
            except ValueError as e:
                print(f"ValueError: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
            finally:
                conn.close()
                print("Connection closed.")

if __name__ == "__main__":
    main()
