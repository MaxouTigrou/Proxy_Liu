# -*- coding: latin-1 -*-
import socket
import threading

# Define the proxy server's IP address and port
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8888

def handle_client(client_socket):
    request_data = client_socket.recv(16384)
    print(f"Received request:\n{request_data.decode('utf-8')}")
    
    #Check if it's a GET method, else pass
    if b'GET' not in request_data :
        print("Not a GET Method")
        return;

    # Extract the destination web server and port from the request
    dest_host, dest_port = extract_destination(request_data.decode('utf-8'))
    

    # Create a socket to connect to the destination web server
    dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest_socket.connect((dest_host, dest_port))

    # Forward the request to the destination server
    dest_socket.send(request_data)

    # Receive and forward the response from the destination server in binary
    response_data = b''
    while True:
        data = dest_socket.recv(16384)
        if len(data) == 0:
            break
        response_data += data
    
    # Check if the response is a 304 Not Modified
    if b'HTTP/1.1 304 Not Modified' in response_data:
        # Create a custom error page for 304 responses
        error_page = b'HTTP/1.1 200 OK\r\n\r\n'
        error_page += b'Proxy server error: Refresh your cache'
        client_socket.send(error_page)
    else:
        # Modify pages in this order : 
        # * Replace Stockolm with Linkoping
        # * Replace Smiley with Trolly
        # * Replace Smiley image with Trolly image
        # * Correct error "Linkoping-spring"
        modified_response = response_data.replace(b'Stockholm', b'Linkoping')
        modified_response = modified_response.replace(b'Smiley', b'Trolly')
        modified_response = modified_response.replace(b'href="./smiley.jpg"', b'href="http://zebroid.ida.liu.se/fakenews/trolly.jpg"')
        modified_response = modified_response.replace(b'src="./smiley.jpg"', b'src="http://zebroid.ida.liu.se/fakenews/trolly.jpg"')
        modified_response = modified_response.replace(b'src="./smiley.jpg"', b'src="http://zebroid.ida.liu.se/fakenews/trolly.jpg"')
        modified_response = modified_response.replace(b'src="./Linkoping-spring.jpg"', b'src="./Stockholm-spring.jpg"')
    
        #Send modify contenent
        client_socket.send(modified_response)

    # Close the sockets
    client_socket.close()
    dest_socket.close()

def extract_destination(request_str):
    # Initialize variables to store the host and port
    host = ''
    port = 80

    # Split the HTTP request string into lines
    lines = request_str.split('\n')
    for line in lines:
        # Check if the line starts with 'Host: '
        if line.startswith('Host: '):
            # Split the line into words separated by spaces and retrieve the second word (host and port)
            host_port = line.strip().split(' ')[1]
            # Check if the port is specified (if there is a ':' in host/port)
            if ':' in host_port:
                # If yes, split the host and port using ':' as a separator
                host, port = host_port.split(':')
                # Convert the port to an integer
                port = int(port)
            else:
                # If the port is not specified, simply use the host
                host = host_port

    # Return the extracted host and port as a tuple (host, port)
    return host, port

def main():

    #SETUP the proxy IP and PORT
    print("\n====================SETUP====================")
    
    PROXY_HOST = str(input("Choose your IP (default : 127.0.0.1) \n"))
    PROXY_PORT = int(input("Choose your PORT (default : 8888) \n"))
    
    
    print("\n====================PROXY====================")
    # Create a socket to listen for incoming client connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((PROXY_HOST, PROXY_PORT))
    server.listen(5)
    print(f"Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        # Create a new thread to handle the client's request
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()