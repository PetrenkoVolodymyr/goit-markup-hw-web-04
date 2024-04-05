from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import socket
import threading
import json
import logging
import datetime

HOST = '127.0.0.1'
PORT = 5000

def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')
            save_data_from_form(data)
                # sock.sendto(data, address)
                # print(f'Send data: {data.decode()} to: {address}')

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def save_data_from_form(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        all_data = {}
        current_time=datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        with open('storage/data.json', 'r', encoding='utf-8') as file:
            all_data = json.loads(file.read())
        print(f'BEFORE: {all_data}')
        parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
        all_data[current_time]=parse_dict
        with open('storage/data.json', 'w', encoding='utf-8') as file:
            json.dump(all_data, file, ensure_ascii=False, indent=4)
        print(f'ALLL DATA: {all_data}')

    except ValueError as err:
        logging.error(err)
    except OSError as err:
        logging.error(err)


def run_client(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    # for line in MESSAGE.split(' '):
        # data = line.encode()
    sock.sendto(data, server)
    print(f'Send data: {data.decode()} to server: {server}')
    # response, address = sock.recvfrom(1024)
    # print(f'Response data: {response.decode()} from address: {address}')
    sock.close()


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        run_client(HOST, PORT, data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    # run()
    server = threading.Thread(target=run_server, args=(HOST, PORT))
    httpServer = threading.Thread(target=run, args=(HTTPServer, HttpHandler))

    server.start()
    httpServer.start()
    server.join()
    httpServer.join()
    # print('Done!')