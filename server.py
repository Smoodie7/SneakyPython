import socket
import threading

import re
from os import system, name


def basic_commands(command):
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
    else:
        print("[!] Incorrect syntax. (maybe your forgot '/'?)")


def handle_client(client_socket):
    client_socket.settimeout(10)

    while True:
        response = input(">>")
        if re.match(r'^/', response):
            response = re.sub(r'^/', '', response)
            print("[*] Sending..")
            client_socket.send(bytes(response, 'utf-8'))

            data = client_socket.recv(1024)
            if not data:
                break
            print(f"[#] Received: {data.decode('utf-8')}")
        else:
            basic_commands(response.lower())

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
