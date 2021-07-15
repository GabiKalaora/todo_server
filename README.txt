Todo server assignment:

To run the program, run todo_server.py script (to activate server), 
while server is running, run todo_client.py a CLI should open, valid commands are:

$ todo add-task "TASK NAME"  
$ todo update-task "TASK NAME" "NEW TASK NAME"
$ todo complete-task "TASK NAME"    
$ todo undo-task "TASK NAME"     
$ todo delete-task "TASK NAME"
$ todo list-tasks 
$ todo list-completed-tasks

When running the test_todo_server.py run each test case individually since each test case creates a new instance of Server() object. 