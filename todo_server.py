import socket
import threading

FORMAT = 'utf-8'
PORT = 9000
MAX_LEN_MSG = 1024
NAME_COMPLETED_MSG_GAP = 24
ALL_COMMANDS = {'add-task',
                'update-task',
                'complete-task',
                'undo-task',
                'delete-task',
                'list-tasks',
                'list-completed-tasks'
                }

INVALID_COMMAND_MSG = 'ERROR: invalid command'
UPDATE_TASK_ERROR = 'ERROR: cant update completed/non existing task'
ADD_TASK_ERROR = 'ERROR: task all ready in list'
COMPLETE_TASK_ERROR = 'ERROR: cant complete completed/non existing task'
UNDO_TASK_ERROR = 'ERROR: cant undo non completed task'
DELETE_MSG_ERROR = 'ERROR: cant delete a non existing task'
NO_COMPLETED_TASKS_ERROR = 'No completed tasks exist'


class Server:
    # create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # all data is global and holds data of all clients
    all_data = dict()
    connections = []

    def __init__(self):
        self.SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
        self.PORT = PORT

    def run(self):
        """
        starts and activates server and waiting for clients to connect and send commands
        """
        # connect to server_address via port 
        self.sock.bind((self.SERVER_ADDRESS, self.PORT))
        # wait for clients to connect
        self.sock.listen()
        print('listening on:', self.SERVER_ADDRESS)

        while True:
            client, client_addr_and_port = self.sock.accept()
            self.connections.append((client, str(client_addr_and_port[0])))

            # create a distinct key for each client
            key = str(client_addr_and_port[0]) + 'id' + str(len(self.connections))
            # create thread so server can handle clients command and still be activated for other clients
            c_thread = threading.Thread(target=self.handler, args=(client, client_addr_and_port, key))
            c_thread.daemon = True
            c_thread.start()

            # create data structure for client with distinct key
            self.all_data[key] = {'all_tasks': [], 'completed': []}
            # print in server who had been connected
            print(str(client_addr_and_port[0]) + ':' + str(client_addr_and_port[1]), 'connected')

    def handler(self, client, client_addr_and_port, key):
        """
        handles communication with this clients current command
        :param client: to handle his command
        :param client_addr_and_port
        :param key: to access data of this client
        """
        while True:
            # get data from client
            data = client.recv(MAX_LEN_MSG)
            # validate data
            invalid_task = self.invalid_task(str(data, FORMAT))
            if not invalid_task:
                # add data to this client data holder
                self.command_handler(str(data, FORMAT), key, client)
            else:
                client.send(invalid_task.encode(FORMAT))

    def invalid_task(self, line):
        """
        validates clients command and calls relevant functions
        :param line: clients command
        :return: failure msg if command is invalid
        """
        parsed_line = line.split()
        if parsed_line[0] != 'todo' or len(parsed_line) < 2:
            return INVALID_COMMAND_MSG

        if parsed_line[1] not in ALL_COMMANDS:
            return INVALID_COMMAND_MSG

    def generate_msg(self, msg, c):
        """
        send msg to client c
        """
        c.send(msg.encode(FORMAT))

    def command_handler(self, line, key, c):
        """
        if command structure is valid, this func will run clients command with clients data base
        and call for each case its relevant function
        :param line: command to process
        :param key: who sended the command
        :param c: client that have sent this command
        """
        temp = line
        line = line.replace('"', '')
        parsed_command = line.split()

        if parsed_command[1] == 'add-task':
            ret_val = self.add_task_case(key, parsed_command)
            if ret_val == ADD_TASK_ERROR:
                self.generate_msg(ADD_TASK_ERROR, c)
            else:
                self.all_data[key]['all_tasks'].append(ret_val)

        elif parsed_command[1] == 'update-task':
            ret_val = self.update_task_case(key, temp)
            if ret_val == UPDATE_TASK_ERROR:
                self.generate_msg(UPDATE_TASK_ERROR, c)
            else:
                self.all_data[key]['all_tasks'][ret_val[1]] = ret_val[0]

        elif parsed_command[1] == 'complete-task':
            ret_val = self.complete_task_case(key, parsed_command)
            if ret_val == COMPLETE_TASK_ERROR:
                self.generate_msg(COMPLETE_TASK_ERROR, c)
            else:
                self.all_data[key]['completed'].append(ret_val)

        elif parsed_command[1] == 'undo-task':
            ret_val = self.undo_task_case(key, parsed_command)
            if ret_val == UNDO_TASK_ERROR:
                self.generate_msg(UNDO_TASK_ERROR, c)
            else:
                self.all_data[key]['completed'].remove(ret_val)

        elif parsed_command[1] == 'delete-task':
            ret_val = self.delete_task_case(key, parsed_command)
            if ret_val == DELETE_MSG_ERROR:
                self.generate_msg(DELETE_MSG_ERROR, c)
            else:
                self.all_data[key]['all_tasks'].remove(ret_val)

        elif parsed_command[1] == 'list-tasks':
            ret_val = self.list_tasks_case(key, c, parsed_command)
            if ret_val == INVALID_COMMAND_MSG:
                self.generate_msg(INVALID_COMMAND_MSG, c)

        elif parsed_command[1] == 'list-completed-tasks':
            ret_val = self.list_completed_tasks_case(key, c, parsed_command)
            if ret_val == INVALID_COMMAND_MSG:
                self.generate_msg(INVALID_COMMAND_MSG, c)
            if ret_val == NO_COMPLETED_TASKS_ERROR:
                self.generate_msg(NO_COMPLETED_TASKS_ERROR, c)

    def add_task_case(self, client_key, parsed_data):
        """
        add_task_case checks if task not in list
        """
        task = ' '.join(parsed_data[2:])
        if task in self.all_data[client_key]['all_tasks']:
            return ADD_TASK_ERROR
        else:
            return task

    def update_task_case(self, client_key, temp):
        """
        checks if command format is valid and if old task is in tasks list
        """
        temp = temp.split('"')
        if len(temp) < 4:
            return UPDATE_TASK_ERROR
        old_task, new_task = temp[1], temp[3]
        if old_task not in self.all_data[client_key]['all_tasks'] or \
                old_task in self.all_data[client_key]['completed']:
            return UPDATE_TASK_ERROR
        else:
            for i in range(len(self.all_data[client_key]['all_tasks'])):
                if old_task == self.all_data[client_key]['all_tasks'][i]:
                    return new_task, i

    def complete_task_case(self, client_key, parsed_data):
        """
        checks if task to complete is in tasks list and not completed all ready
        """
        task = ' '.join(parsed_data[2:])
        if task not in self.all_data[client_key]['all_tasks'] or \
                task in self.all_data[client_key]['completed']:
            return COMPLETE_TASK_ERROR
        else:
            return task

    def undo_task_case(self, client_key, parsed_data):
        """
        checks if task is in completed tasks and in list of tasks
        """
        task = ' '.join(parsed_data[2:])
        if task not in self.all_data[client_key]['completed'] or \
                task not in self.all_data[client_key]['all_tasks']:
            return UNDO_TASK_ERROR
        else:
            return task

    def delete_task_case(self, client_key, parsed_data):
        """
        checks if task is in tasks list
        """
        task = ' '.join(parsed_data[2:])
        if task not in self.all_data[client_key]['all_tasks']:
            return DELETE_MSG_ERROR
        else:
            return task

    def list_tasks_case(self, client_key, c, parsed_data):
        """
        checks if command format is right and generates the list of tasks
        """
        if len(parsed_data) != 2:
            return INVALID_COMMAND_MSG
        else:
            self.generate_msg('NAME               COMPLETED', c)
            for task in self.all_data[client_key]['completed']:
                gap = ' ' * (NAME_COMPLETED_MSG_GAP - len(task))
                self.generate_msg(f'{task}{gap}+', c)
                self.generate_msg('\n', c)

            for task in set(self.all_data[client_key]['all_tasks']) - set(self.all_data[client_key]['completed']):
                gap = ' ' * (NAME_COMPLETED_MSG_GAP - len(task))
                self.generate_msg(f'{task}{gap}-', c)
                self.generate_msg('\n', c)

    def list_completed_tasks_case(self, client_key, c, parsed_data):
        """
        checks format of command and generates list of completed tasks if exists
        """
        if len(parsed_data) != 2:
            return INVALID_COMMAND_MSG
        else:
            if len(self.all_data[client_key]['completed']) == 0:
                return NO_COMPLETED_TASKS_ERROR
            else:
                self.generate_msg('NAME               COMPLETED', c)
                for task in self.all_data[client_key]['completed']:
                    gap = ' ' * (NAME_COMPLETED_MSG_GAP - len(task))
                    self.generate_msg(f'{task}{gap}+', c)
                    self.generate_msg('\n', c)


if __name__ == '__main__':
    server = Server()
    server.run()
