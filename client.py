import socket

def send_range_and_receive_results(start, end, server_address):
    try:
        # Open a socket connection outside the 'with' statement to maintain scope
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Attempting to connect to master server at {server_address}...")
        s.connect(server_address)
        print("Connection established.")
        
        # Prepare and send the data range to the server
        message = f"{start},{end}".encode()
        s.sendall(message)
        print(f"Sent to server: {start} to {end}")
        
        # Keep receiving data until the connection is closed
        while True:
            result = s.recv(1024)  # Adjust buffer size if needed
            if not result:
                print("No more data received. Server may have closed the connection.")
                break  # No more data, server has closed connection
            print("Received from server:")
            print(result.decode())
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        s.close()  # Ensure the socket is closed properly

def main():
    try:
        start, end = map(int, input("Enter start and end of range: ").split())
    except ValueError:
        print("Invalid input. Please enter two integers.")
        return

    server_address = ('192.168.100.4', 10001)  # IP and port of the master server
    send_range_and_receive_results(start, end, server_address)

if __name__ == "__main__":
    print("Client is running...")
    main()
