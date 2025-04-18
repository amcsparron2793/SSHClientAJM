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


class SSHClient:
    """
    Represents an SSH client for establishing secure connections and performing
    remote operations on a host. This class makes use of the `paramiko` library
    to manage SSH connections and provide an interactive shell for command
    execution.

    The purpose of this class is to simplify the process of connecting to a
    remote server via SSH, handle user authentication, and enable a shell-like
    interface for input and output over the established session.

    :ivar hostname: The hostname or IP address of the server to connect to.
    :type hostname: str
    :ivar port: The port number for the SSH connection; defaults to 22 if not provided.
    :type port: int
    :ivar username: The username for authenticating the SSH session.
    :type username: str
    :ivar client: A `paramiko.SSHClient` instance used to manage the SSH connection.
    :type client: paramiko.SSHClient
    :ivar _cxn_channel: The communication channel used for the SSH session.
    :type _cxn_channel: paramiko.Channel
    """
    def __init__(self, hostname=None, port=None, **kwargs):
        self.hostname = hostname or input('Please Enter Hostname: ')
        self.port = port or input('Please Enter Port (22): ')
        if not self.port:
            self.port = 22
        self.username = kwargs.get('username', input('Please Enter Username: '))
        self.__password = kwargs.get('password', getpass.getpass('Please Enter Password: '))
        self.client = self.init_client()
        self._cxn_channel = None

    @classmethod
    def connect_and_get_interactive_shell(cls):#, hostname, port, username, password):
        """
        Establishes a connection to the target host and retrieves an interactive shell.
        This method initializes a client, establishes a connection to the specified remote
        host, and then sets up an interactive shell session.

        :return: An instance of the client class with an active interactive shell.
        :rtype: cls
        """
        client = cls()
        client.connect()
        client.get_interactive_shell()

    def init_client(self):
        """
        Initializes and returns an SSH client using Paramiko.

        This function sets up the SSH client to automatically accept missing
        host keys and returns the initialized client instance.

        :return: An initialized SSH client instance.
        :rtype: paramiko.SSHClient
        """
        # Initialize SSH client
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return self.client

    def connect(self):
        """
        Establish an SSH connection to the provided hostname using the specified credentials
        and port. If successful, this method returns the SSH channel.

        If an authentication failure occurs, the connection is closed, and an appropriate
        message is printed. For other exceptions related to the SSH connection, details of
        the exception are printed and the connection is also closed.

        :raises paramiko.AuthenticationException: If the provided credentials are incorrect.
        :raises Exception: For any other errors that occur during the connection process.
        :return: The SSH connection channel.
        :rtype: Any
        """
        try:
            print(f"🔌 Connecting to {self.username}@{self.hostname}:{self.port}...")
            self.client.connect(hostname=self.hostname, port=self.port,
                                username=self.username, password=self.__password)
            self._cxn_channel = self.client.invoke_shell()
            print("✅ Connected.")
            return self._cxn_channel
        except paramiko.AuthenticationException:
            print("❌ Authentication failed.")
            self.close(1)
        except Exception as e:
            print(f"❌ SSH connection error: {e}")
            self.close(1)

    def close(self, exit_code=0):
        """
        Closes the SSH client session and terminates the program.

        This method terminates the active SSH client session, outputs a message
        indicating the closure of the session, and exits the program with the
        specified exit code.

        :param exit_code: The exit code with which the program will terminate.
        :type exit_code: int
        :return: This method does not return any value.
        """
        self.client.close()
        print("🔒 SSH session closed.")
        exit(exit_code)

    def get_interactive_shell(self):
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

        writer = threading.Thread(target=writeall, args=(self._cxn_channel,))
        writer.daemon = True
        writer.start()

        try:
            while True:
                # Read user input and send it to the server
                command = sys.stdin.readline()
                if not command:
                    break
                self._cxn_channel.send(command)
        except KeyboardInterrupt:
            print("\n✋ Disconnected by user.")
        finally:
            self._cxn_channel.close()



if __name__ == "__main__":
    # default_test_options = {
    #     "hostname": input('Enter your SSH server hostname or IP address: '),
    #     "port":22,
    #     "username": input('Enter your SSH username: '),
    #     "password": getpass.getpass("Enter your SSH password: ")
    # }

    # this is how to connect without using the class method
    # client = SSHClient(**default_test_options)
    # client.connect()
    # client.get_interactive_shell()
    SSHClient.connect_and_get_interactive_shell()
