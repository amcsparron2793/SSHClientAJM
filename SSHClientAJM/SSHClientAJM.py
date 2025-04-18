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
from typing import Optional

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
    :ivar _connection_channel: The communication channel used for the SSH session.
    :type _connection_channel: paramiko.Channel
    """

    def __init__(self, hostname: Optional[str] = None, port: Optional[int] = None, **kwargs):
        self.hostname: str = hostname
        self.port: int = port or 22
        self.username: Optional[str] = kwargs.get('username', None)
        self.__password: Optional[str] = kwargs.get('password', None)
        self.client: Optional[paramiko.SSHClient] = self.init_client()
        self._connection_channel: Optional[paramiko.Channel] = None
        self._set_defaults()

    def _set_defaults(self):
        """Sets default values for attributes if they are not provided."""
        if not self.hostname:
            self.hostname = input('Please Enter Hostname: ')
        if not self.username:
            self.username = input('Please Enter Username: ')
        if not self.__password:
            self.__password = getpass.getpass('Please Enter Password: ')

    @classmethod
    def connect_and_get_interactive_shell(cls):#, hostname, port, username, password):
        """
        Establishes a connection to the target host and retrieves an interactive shell.
        This method initializes a client, establishes a connection to the specified remote
        host, and then sets up an interactive shell session.

        :return: An instance of the client class with an active interactive shell.
        :rtype: cls
        """
        c = cls()
        c.connect()
        c.get_interactive_shell()

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

    @property
    def is_connected(self):
        try:
            return self.client.get_transport().is_active()
        except AttributeError:
            return False

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
            self._connection_channel = self.client.invoke_shell()
            print("✅ Connected.")
            return self._connection_channel
        except paramiko.AuthenticationException:
            print("❌ Authentication failed.")
            self.close(1)
        except Exception as e:
            print(f"❌ SSH connection error: {e}")
            self.close(1)

    def send_command(self, command: str) -> str:
        """
        Executes a single command on the remote server and captures its output.
    
        This method sends a command over the SSH connection using `exec_command`,
        waits for the command to complete, and retrieves the output and error streams.
    
        :param command: The command to execute over the SSH connection.
        :type command: str
        :return: The command output (stdout) and error output (stderr), concatenated as a string.
        :rtype: str
        :raises Exception: If the client is not connected or if an error occurs during execution.
        """
        if not self.is_connected:
            raise Exception("Not connected to the server. Call `connect()` first.")

        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            stdout_content = stdout.read().decode().strip()
            stderr_content = stderr.read().decode().strip()

            if stderr_content:
                return f"STDOUT:\n{stdout_content}\n\nSTDERR:\n{stderr_content}"
            return stdout_content

        except Exception as e:
            raise Exception(f"Failed to execute command '{command}': {e}")

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

    @staticmethod
    def _write_all_to_stdout(sock):
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

    def _start_writer_daemon(self):
        """
        Starts a writer daemon thread that handles output redirection by writing data
        from the provided connection channel to the standard output.

        This function initializes a daemon thread that repeatedly writes all data
        retrieved from the connection channel to the standard output stream. The
        thread is marked as a daemon to ensure it terminates automatically when the
        main program exits. The thread execution is delegated to the target method
        `_write_all_to_stdout`, which processes the specified connection channel.

        :param self: The instance of the class that invokes this method.
        :return: None
        """
        writer = threading.Thread(target=self._write_all_to_stdout, args=(self._connection_channel,))
        writer.daemon = True
        writer.start()

    def _stream_loop(self, command=None):
        """
        Executes a loop for continuously processing commands. If a command is not provided,
        it reads input from the user, appends a newline, and sends it to the server through
        the connected channel. This process runs indefinitely until interrupted or a breaking
        condition is met. The method ensures resources are properly cleaned up after execution.

        :param command: The initial command to be sent to the server. If None, the method
            will read user input instead. Defaults to None.
        :return: None
        """
        try:
            while True:
                if not command:
                    # Read user input and send it to the server
                    command = sys.stdin.readline()
                else:
                    command = command + "\n"
                if not command:
                    break
                self._connection_channel.send(command)
                command = None
        except KeyboardInterrupt:
            print("\n✋ Disconnected by user.")
        finally:
            self.close(0)
            # self._connection_channel.close()

    def get_interactive_shell(self):
        """
        Provides an interactive shell for an SSH connection. This method ensures
        that the connection is established before initiating the shell. It also starts
        a writer daemon and enters a streaming loop to handle real-time data transfers
        within the SSH session. The interactive shell allows for sending and receiving
        commands or data dynamically.

        :raises paramiko.SSHException: If the SSH client is not connected to the server,
            indicating that the user must connect before attempting to open an
            interactive shell.
        """
        if not self.is_connected:
            raise paramiko.SSHException("Not connected to server, connect first")

        self._start_writer_daemon()
        self._stream_loop()

    def non_interactive_stream(self, command):
        """
        Executes a command over an SSH connection in a non-interactive manner. This
        method requires the SSH connection to already be established before being
        called. It starts a writer daemon to handle the process and runs a streaming
        loop for the provided command.

        :param command: Command to be executed on the remote server.
        :type command: str
        :raises paramiko.SSHException: If the SSH connection is not established.
        :return: None
        """
        if not self.is_connected:
            raise paramiko.SSHException("Not connected to server, connect first")

        self._start_writer_daemon()
        self._stream_loop(command)





if __name__ == "__main__":
    pihole_command = "sudo pihole -t | grep --color=always -Ei 'query|blocked'"

    # this is how to connect without using the class method
    client = SSHClient(hostname="192.168.1.121", port=22)#**default_test_options)
    client.connect()
    client.get_interactive_shell()
    # print(client.send_command("sudo pihole -t"))
    #client.non_interactive_stream(command=pihole_command)


    # SSHClient.connect_and_get_interactive_shell()
