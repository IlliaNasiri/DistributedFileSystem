import socket
from http_request import HttpRequest
import pickle
import json
import threading


class MetaServer:
    def __init__(self, host, port):
        print(host)
        self.host = host
        self.port = port
        # a TCP socket, supporting IPv4
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # TODO: CHANGE THIS TO BE USER CONFIGURABLE
        self.nodes = [("192.168.157.38", 8001), (self.host, 8002)]

    def start_server(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f'Meta server listening on {self.host}:{self.port}')

        while True:
            conn, addr = self.server.accept()
            request = HttpRequest(conn.recv(2048).decode())

            if request.get_request_length() > 0:
                # Handle requests using other threads
                if request.get_request_type() == 'GET' and request.get_file_path() == "":
                    threading.Thread(target=self.list_files, args=(conn, addr), daemon=True).start()

                elif request.get_request_type() == 'GET':
                    threading.Thread(target=self.get_file, args=(conn, addr, request.get_file_path()), daemon=True).start()

                elif request.get_request_type() == 'POST':
                    self.upload_file()

    def list_files(self, conn, addr):
        files = self.__list_files()
        print(files)
        files = list(files.keys())
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += json.dumps(files)
        conn.send(response.encode())
        conn.close()

    def get_file(self, conn, addr, path):
        files_dict = self.__list_files()
        if path not in files_dict.keys():
            print("NOT FOUND 11111")
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"

        else:
            node = files_dict.get(path)

            msg = f'GET /{path} HTTP/1.1\r\n'
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(node)
            client.send(msg.encode())
            # redirect!
            response = client.recv(2048).decode()


        conn.send(response.encode())
        conn.close()

    def upload_file(self):
        pass



    def add_node(self):
        pass

    def remove_node(self):
        pass

    def list_nodes(self):
        pass

    def __list_files(self):
        files = {}
        threads = []
        lock = threading.Lock()

        def obtain_list_of_files_of_node(node, files, lock):
            msg = "GET / HTTP/1.1\r\n"

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(node)
            client.send(msg.encode())

            files_list = []
            with lock:
                files_list = pickle.loads(client.recv(2048))
                for file in files_list:
                    files[file] = node

        for node in self.nodes:
            t = threading.Thread(target=obtain_list_of_files_of_node, args=(node, files, lock), daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return files


meta_server = MetaServer('192.168.157.164', 8000)
meta_server.start_server()
