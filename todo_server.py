import socket
import threading

FORMAT = 'utf-8'
PORT = 9000
MAX_LEN_MSG = 1024
GAP = 24
ALL_COMMANDS = {'add-task',
                'update-task',
                'complete-task',
                'undo-task',
                'delete-task',
                'list-tasks',
                'list-completed-tasks'
                }
VALID_COMMANDS = """Usage :-
            $ todo add-task "TASK NAME"  
            $ todo update-task "TASK NAME" "NEW TASK NAME"
            $ todo complete-task "TASK NAME"    
            $ todo undo-task "TASK NAME"     
            $ todo delete-task "TASK NAME"
            $ todo list-tasks 
            $ todo list-completed-tasks"""

INVALID_COMMAND_MSG = 'ERROR: invalid command'
UPDATE_TASK_ERROR = 'ERROR: cant update completed/non existing task'
ADD_TASK_ERROR = 'ERROR: task all ready in list'
COMPLETE_TASK_ERROR = 'ERROR: cant complete this task'
UNDO_TASK_ERROR = 'ERROR: cant undo non completed/non existing task'
DELETE_MSG_ERROR = 'ERROR: cant delete a non existing task'


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    all_data = dict()

    def __init__(self):
        self.SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
        self.PORT = PORT
        self.sock.bind((self.SERVER_ADDRESS, self.PORT))
        self.sock.listen()

    def handler(self, c, a):
        while True:
            # get data from client
            data = c.recv(MAX_LEN_MSG)
            # validate data
            invalid_task = self.invalid_task(str(data, FORMAT))
            if not invalid_task:
                # add data to this client data holder
                key = str(a[1])
                self.valid_command_handler(str(data, FORMAT), key, c)
            else:
                c.send(invalid_task.encode(FORMAT))

            # TODO: this part is not working
            if not data:
                print(str(a[0]) + ':' + str(a[1]), 'disconnected')
                self.connections.remove(c)
                c.close()
                break

    def run(self):
        print('listening on:', self.SERVER_ADDRESS)
        while True:
            c, a = self.sock.accept()
            c_thread = threading.Thread(target=self.handler, args=(c, a))
            c_thread.daemon = True
            c_thread.start()
            self.connections.append((c, str(a[0])))
            key = str(a[1])
            self.all_data[key] = {'all_tasks': [], 'completed': []}
            # print for user who had been connected
            print(str(a[0]) + ':' + str(a[1]), 'connected')

    def invalid_task(self, line):
        # TODO: cover all invalid cases
        parsed_line = line.split()
        if parsed_line[0] != 'todo' or len(parsed_line) < 2:
            return INVALID_COMMAND_MSG

        if parsed_line[1] not in ALL_COMMANDS:
            return INVALID_COMMAND_MSG

    def generate_msg(self, msg, c):
        c.send(msg.encode(FORMAT))

    def valid_command_handler(self, line, client, c):
        temp = line
        line = line.replace('"', '')
        parsed_data = line.split()

        if parsed_data[1] == 'add-task':
            task = ' '.join(parsed_data[2:])
            if task in self.all_data[client]['all_tasks']:
                self.generate_msg(ADD_TASK_ERROR, c)
            else:
                self.all_data[client]['all_tasks'].append(task)

        elif parsed_data[1] == 'update-task':
            temp = temp.split('"')
            old_task, new_task = temp[1], temp[3]
            if old_task not in self.all_data[client]['all_tasks'] or \
                    old_task in self.all_data[client]['completed']:
                self.generate_msg(UPDATE_TASK_ERROR, c)
            else:
                for i in range(len(self.all_data[client]['all_tasks'])):
                    if old_task == self.all_data[client]['all_tasks'][i]:
                        self.all_data[client]['all_tasks'][i] = new_task

        elif parsed_data[1] == 'complete-task':
            task = ' '.join(parsed_data[2:])
            if task not in self.all_data[client]['all_tasks'] or \
                    task in self.all_data[client]['completed']:
                self.generate_msg(COMPLETE_TASK_ERROR, c)
            else:
                self.all_data[client]['completed'].append(task)

        elif parsed_data[1] == 'undo-task':
            task = ' '.join(parsed_data[2:])
            if task not in self.all_data[client]['completed'] or \
                    task not in self.all_data[client]['all_tasks']:
                self.generate_msg(UNDO_TASK_ERROR, c)
            else:
                self.all_data[client]['completed'].remove(task)

        elif parsed_data[1] == 'delete-task':
            task = ' '.join(parsed_data[2:])
            if task not in self.all_data[client]['all_tasks']:
                self.generate_msg(DELETE_MSG_ERROR, c)
            else:
                self.all_data[client]['all_tasks'].remove(task)

        elif parsed_data[1] == 'list-tasks':
            if len(parsed_data) != 2:
                self.generate_msg(INVALID_COMMAND_MSG, c)
            else:
                # TODO: design the list all_task msg and send to client
                self.generate_msg('NAME               COMPLETED', c)
                for task in self.all_data[client]['completed']:
                    gap = ' ' * (GAP - len(task))
                    self.generate_msg(f'{task}{gap}+', c)
                    self.generate_msg('\n', c)

                for task in set(self.all_data[client]['all_tasks']) - set(self.all_data[client]['completed']):
                    gap = ' ' * (GAP - len(task))
                    self.generate_msg(f'{task}{gap}-', c)
                    self.generate_msg('\n', c)

        elif parsed_data[1] == 'list-completed-tasks':
            if len(parsed_data) != 2:
                self.generate_msg(INVALID_COMMAND_MSG, c)
            else:
                # TODO: design the list completed msg and send to client
                if len(self.all_data[client]['completed']) == 0:
                    self.generate_msg('No completed tasks exist', c)
                else:
                    self.generate_msg('NAME               COMPLETED', c)
                    for task in self.all_data[client]['completed']:
                        gap = ' ' * (GAP - len(task))
                        self.generate_msg(f'{task}{gap}+', c)
                        self.generate_msg('\n', c)
        else:
            # TODO: generate a msg with all valid operands
            self.generate_msg(VALID_COMMANDS, c)


server = Server()
server.run()
