import socket
from http_request import HttpRequest
import os
import pickle
import sys
import threading


class NodeServer:
    def __init__(self, host, port, managed_folder):
        self.host = host
        self.port = port
        # a TCP socket, supporting IPv4
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # TODO: CHANGE THIS TO BE USER CONFIGURABLE
        self.managed_folder = managed_folder

    def start_server(self):
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        print(f'Node server listening on {self.host}:{self.port}')

        while True:
            conn, addr = self.server.accept()
            request = HttpRequest(conn.recv(2048).decode())

            if request.get_request_length() > 0:
                # TODO: ADD ABILITY TO CHECK INSIDE FOLDERS
                if request.get_request_type() == 'GET' and request.get_file_path() == "":
                    threading.Thread(target=self.list_files, args=(conn, addr), daemon=True).start()

                elif request.get_request_type() == 'GET':
                    # self.get_file(request.get_file_path())
                    threading.Thread(target=self.get_file, args=(request.get_file_path(), conn, addr),
                                     daemon=True).start()

                elif request.get_request_type() == 'POST':
                    self.upload_file()

    def list_files(self, conn, addr):
        file_dir_list = os.listdir(self.managed_folder)
        pickle_file_dir_list = pickle.dumps(file_dir_list)
        conn.send(pickle_file_dir_list)
        conn.close()
        return

    def upload_file(self):
        pass

    def get_file(self, file_path, conn, addr):
        response = ""
        file_path = os.path.join(self.managed_folder, file_path)
        if os.path.isfile(file_path):
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
            response += "\r\n"

            with open(file_path, 'r') as file:
                response += file.read()
        else:
            print("NOT FOUND!")
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"

        conn.send(response.encode())
        conn.close()

    def add_node(self):
        pass

    def remove_node(self):
        pass

    def list_nodes(self):
        pass


node_server = NodeServer('192.168.157.164', 8002, sys.argv[2])
node_server.start_server()
