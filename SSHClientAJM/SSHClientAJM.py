"""
SSHClientAJM.py

This script provides functionality for establishing an interactive SSH session with a remote server.
It utilizes the Paramiko library to manage SSH connections and perform authentication. The primary
goal of the script is to allow users to securely connect to remote servers, execute commands interactively,
and view real-time responses through an interactive shell-like interface.

Key Features:
- Establishes an SSH connection to a remote server using user-provided credentials.
- Provides an interactive shell for executing commands and viewing responses.
- Handles authentication errors and connection issues gracefully.
- Ensures secure connections by managing host keys (using AutoAddPolicy for demonstration purposes).

The script is designed as a standalone utility and can be executed directly. Users will be prompted for the
necessary details (hostname, username, and password) to initiate the SSH connection.
"""

from _version import __version__

import paramiko
import sys
import threading
import getpass


def interactive_shell(channel):
    """
    Provides functionality to create an interactive shell over a given channel.

    The `interactive_shell` function enables users to send commands to a server
    by leveraging a continuous input/output shell-like interface. It spawns a
    thread to handle incoming data from the server while allowing the user to
    send commands interactively.

    :param channel: A communication channel (e.g., a socket or SSH channel) for
        reading responses and sending commands.
    :type channel: Any
    """
    def writeall(sock):
        """
        Handles continuous reading of data from a socket and displays it on the
        standard output. The function reads data in chunks and terminates when no
        more data is available from the socket.

        :param sock: The socket object used for receiving data.
        :type sock: socket.socket
        """
        while True:
            data = sock.recv(1024)
            if not data:
                break
            sys.stdout.write(data.decode())
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(channel,))
    writer.daemon = True
    writer.start()

    try:
        while True:
            # Read user input and send it to the server
            command = sys.stdin.readline()
            if not command:
                break
            channel.send(command)
    except KeyboardInterrupt:
        print("\n✋ Disconnected by user.")
    finally:
        channel.close()

def ssh_connect_interactive(hostname, port, username, password):
    """
    Establishes an SSH connection to the specified host and starts an interactive shell session.

    This function uses the Paramiko library to create an SSH connection. It initializes the
    client, sets the host key policy, and connects to the remote host using the provided
    credentials. Upon successful connection, the function invokes an interactive shell
    session on the remote server. If authentication fails or any other exception occurs,
    it handles the error gracefully and ensures the SSH session is closed properly.

    :param hostname: The hostname or IP address of the target SSH server.
    :type hostname: str
    :param port: The port number for the SSH connection.
    :type port: int
    :param username: The username for authentication.
    :type username: str
    :param password: The password for authentication.
    :type password: str
    :return: None. The function does not return a value.
    :rtype: None
    """
    try:
        # Initialize SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"🔌 Connecting to {username}@{hostname}:{port}...")
        client.connect(hostname=hostname, port=port, username=username, password=password)
        print("✅ Connected. Starting interactive shell...\n")

        # Get interactive shell
        channel = client.invoke_shell()
        interactive_shell(channel)

    except paramiko.AuthenticationException:
        print("❌ Authentication failed.")
    except Exception as e:
        print(f"❌ SSH connection error: {e}")
    finally:
        client.close()
        print("🔒 SSH session closed.")

if __name__ == "__main__":
    default_test_options = {
        "hostname": input('Enter your SSH server hostname or IP address: '),
        "port":22,
        "username": input('Enter your SSH username: ')
    }
    print(f"Connecting to {default_test_options['hostname']}:{default_test_options['port']} as {default_test_options['username']}")
    # Replace with your actual SSH server details
    ssh_connect_interactive(
        ** default_test_options,
        password=getpass.getpass("Enter your SSH password: "),
    )
