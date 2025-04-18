# <u>SSHClientAJM</u>
### <i>Provides functionality for establishing an interactive SSH session with a remote server.</i>


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