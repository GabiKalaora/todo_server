import unittest
import todo_server as ts
import todo_client as tc


class TestServer(unittest.TestCase):
    """/
    *** RUN EACH TEST INDIVIDUALLY ***
    since we create an instance of server for each test calling them all
    together will create issues
    /"""

    def test_invalid_task(self):
        server = ts.Server()
        self.assertEqual(server.invalid_task('Im an invalid command'), ts.INVALID_COMMAND_MSG)
        self.assertEqual(server.invalid_task('q'), ts.INVALID_COMMAND_MSG)
        self.assertEqual(server.invalid_task('todo add-takk "learn"'), ts.INVALID_COMMAND_MSG)
        self.assertEqual(server.invalid_task('todo'), ts.INVALID_COMMAND_MSG)

    def test_add_task_case(self):
        """
        check that data base adds commands or sends error msg if command is all ready in data base
        :return:
        """
        server, client = ts.Server(), tc.Client()
        key = client.CLIENT_ADDRESS + 'id1'
        server.all_data[key] = {'all_tasks': [], 'completed': []}
        server.all_data[key]['all_tasks'].extend(['learn', 'code', 'test'])

        commands_all_ready_in_data = ['todo add-task learn', 'todo add-task code', 'todo add-task test']
        for line in commands_all_ready_in_data:
            parsed_data = line.split()
            self.assertEqual(server.add_task_case(key, parsed_data), ts.ADD_TASK_ERROR)

        not_in_data = ['eat', 'sleep']
        commands_not_in_data = ['todo add-task eat', 'todo add-task sleep']
        for command, data in zip(commands_not_in_data, not_in_data):
            parsed_data = command.split()
            self.assertEqual(server.add_task_case(key, parsed_data), data)

    def test_update_task_case(self):
        """
        check that data base updates commands or sends error msg if old_command is not in data base or completed
        """
        server, client = ts.Server(), tc.Client()
        key = client.CLIENT_ADDRESS + 'id1'
        server.all_data[key] = {'all_tasks': [], 'completed': []}
        server.all_data[key]['all_tasks'].extend(['learn', 'code', 'test', 'submit'])
        server.all_data[key]['completed'].extend(['learn', 'code'])

        commands_all_ready_in_data = ['todo update-task "fly" "land" ', 'todo update-task "mode" "dode"',
                                      'todo update-task "learn" "superLearning"']

        for line in commands_all_ready_in_data:
            self.assertEqual(server.update_task_case(key, line), ts.UPDATE_TASK_ERROR)

        valid_command = ['todo update-task "test" "tester"', 'todo add-task "submit" "submited"']
        new_tasks = ['tester', 'submited']
        for command, data in zip(valid_command, new_tasks):
            self.assertEqual(server.update_task_case(key, command)[0], data)

    def test_complete_task_case(self):
        server, client = ts.Server(), tc.Client()
        key = client.CLIENT_ADDRESS + 'id1'
        server.all_data[key] = {'all_tasks': [], 'completed': []}
        server.all_data[key]['all_tasks'].extend(['learn', 'code', 'test'])
        server.all_data[key]['completed'].append('learn')

        commands_completed_or_not_in_list = ['todo complete-task not_in_list', 'todo complete-task learn']
        for line in commands_completed_or_not_in_list:
            parsed_data = line.split()
            self.assertEqual(server.complete_task_case(key, parsed_data), ts.COMPLETE_TASK_ERROR)

        can_complete = ['code', 'test']
        valid_commands = ['todo complete-task code', 'todo complete-task test']
        for command, data in zip(valid_commands, can_complete):
            parsed_data = command.split()
            self.assertEqual(server.complete_task_case(key, parsed_data), data)

    def test_undo_task_case(self):
        server, client = ts.Server(), tc.Client()
        key = client.CLIENT_ADDRESS + 'id1'
        server.all_data[key] = {'all_tasks': [], 'completed': []}
        server.all_data[key]['all_tasks'].extend(['learn', 'code', 'test'])
        server.all_data[key]['completed'].extend(['learn', 'test'])

        commands_not_in_data_or_not_completed = ['todo undo-task not_in_list', 'todo undo-task code']
        for line in commands_not_in_data_or_not_completed:
            parsed_data = line.split()
            self.assertEqual(server.undo_task_case(key, parsed_data), ts.UNDO_TASK_ERROR)

        can_complete = ['learn', 'test']
        valid_commands = ['todo undo-task learn', 'todo undo-task test']
        for command, data in zip(valid_commands, can_complete):
            parsed_data = command.split()
            self.assertEqual(server.undo_task_case(key, parsed_data), data)

    def test_delete_task_case(self):
        server, client = ts.Server(), tc.Client()
        key = client.CLIENT_ADDRESS + 'id1'
        server.all_data[key] = {'all_tasks': [], 'completed': []}
        server.all_data[key]['all_tasks'].extend(['learn', 'code', 'test'])

        commands_not_in_data = ['todo delete-task not_in_list', 'todo delete-task sleep']
        for line in commands_not_in_data:
            parsed_data = line.split()
            self.assertEqual(server.delete_task_case(key, parsed_data), ts.DELETE_MSG_ERROR)

        to_delete = ['learn', 'code']
        command_in_data = ['todo delete-task learn', 'todo delete-task code']
        for line, data in zip(command_in_data, to_delete):
            parsed_data = line.split()
            self.assertEqual(server.delete_task_case(key, parsed_data), data)

    def test_list_tasks_case(self):
        server, client = ts.Server(), tc.Client()
        key = client.CLIENT_ADDRESS + 'id1'
        invalid_commands = ['todo list tasks', 'todo']
        for line in invalid_commands:
            parsed_data = line.split()
            self.assertEqual(server.list_tasks_case(key, client, parsed_data), ts.INVALID_COMMAND_MSG)

    def test_list_completed_tasks_case(self):
        server, client = ts.Server(), tc.Client()
        key = client.CLIENT_ADDRESS + 'id1'
        server.all_data[key] = {'all_tasks': [], 'completed': []}
        invalid_commands = ['todo list completed tasks', 'list-completed-tasks']
        for line in invalid_commands:
            parsed_data = line.split()
            self.assertEqual(server.list_completed_tasks_case(key, client, parsed_data), ts.INVALID_COMMAND_MSG)

        valid_not_completed_tasks = 'todo list-completed-task'
        parsed_data = valid_not_completed_tasks.split()
        self.assertEqual(server.list_completed_tasks_case(key, client, parsed_data), ts.NO_COMPLETED_TASKS_ERROR)


if __name__ == '__main__':
    test_server = TestServer()
    TestServer.test_invalid_task(test_server)
