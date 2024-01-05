import os
import socket
import time

import webbrowser
import re


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_state = False

    while connection_state is False:
        try:
            client.connect(('localhost', 59152))
            connection_state = True
            print("Connected to the server successfully")
        except Exception:
            time.sleep(5)

    main(client)


def main(client):
    while True:
        response = client.recv(1024)
        print(f"Received: {response.decode('utf-8')}")
        decoded_response = response.decode('utf-8')

        match decoded_response:
            case x if "link" in x:  # Opens a link into the default browser
                link_to_open = re.search(r'link\s+(.+)', decoded_response)
                link_to_open = link_to_open.group(1)
                webbrowser.open(link_to_open)

                output = f"{link_to_open} opened with {webbrowser.get().name}"
            case "sysget":
                output = os.uname()
            case "ping":  # Basic ping command
                output = "Pong!!"
            case "close":  # Closing the client
                break
            case _:
                output = "Incorrect syntax."

        client.send(bytes(output, 'utf-8'))

    client.close()


if __name__ == "__main__":
    start_client()
