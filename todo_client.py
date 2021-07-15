import socket
import threading

FORMAT = 'utf-8'
PORT = 9000
MAX_LEN_MSG = 1024


class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_msg(self):
        """
        wait until client inserts a command
        :return:
        """
        while True:
            self.sock.send(bytes(input(''), FORMAT))

    def __init__(self):
        self.CLIENT_ADDRESS = socket.gethostbyname(socket.gethostname())
        self.PORT = PORT
        self.sock.connect((self.CLIENT_ADDRESS, self.PORT))

    def run(self):
        """
        asks for input from client and waits until client inserts a command
        inorder that waiting for command will not block the entire process
        """
        i_thread = threading.Thread(target=self.send_msg)
        i_thread.daemon = True
        i_thread.start()

        while True:
            data = self.sock.recv(MAX_LEN_MSG)
            if not data:
                break
            print(str(data, FORMAT))


if __name__ == '__main__':
    client = Client()
    client.run()
