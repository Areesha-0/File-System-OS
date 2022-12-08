from File_Manager import File_Manager as FM, File, Root, Directory
from Memory_manager import Block, Memory
from treelib import Node, Tree
import threading
import time


class User_Thread (threading.Thread):
    def __init__(self, threadID, name, file_mgr, mem_mgr):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.input_file = "input_thread"+str(self.threadID)+ ".txt"
        self.file_mgr = file_mgr
        self.mem_mgr = mem_mgr
        self.output_file = "output_thread"+str(self.threadID)+ ".txt"

    def run(self):
        print(f"Executing {self.name}")

        commands = self.thread_parser(self.input_file)  # list of commands

        with open(self.output_file, 'a') as fd:

            for command in commands:
                args = command.split(" ")
                inp = args[0]
                output = None

                if inp == "make_dir":
                    dir_name = args[1]
                    output = self.file_mgr.make_directory(dir_name)

                elif inp == "change_dir":
                    dir_name = args[1]
                    output = self.file_mgr.change_dir(dir_name)

                elif inp == "delete_dir":
                    string = input("Enter directory name: ")
                    # for key, value in self.file_mgr.cwd.files_dict.items():
                    #     o_file = self.file_mgr.open_file(key, 'w')
                    #     o_file.truncate_file(o_file.size, self.mem_mgr)
                    self.file_mgr.change_dir(string)
                    output = self.file_mgr.delete_dir(string)

                elif inp == "create_file":
                    f_name = args[1]
                    output = self.file_mgr.create_file(args[1])

                elif inp == "delete_file":
                    f_name = args[1]
                    o_file,str = self.file_mgr.open_file(fname, 'w')
                    o_file.truncate_file(o_file.size, self.mem_mgr)
                    output = self.file_mgr.delete_file(fname)

                elif inp == "move_file":
                    fname = args[3]
                    src_dir = args[1]
                    dest_dir = args[2]
                    output = self.file_mgr.move_file(src_dir, dest_dir, fname)

                elif inp == "open_file":
                    f_name = args[1]
                    mode = args[2]
                    o_file,output = self.file_mgr.open_file(f_name, mode)

                elif inp == "write_to_file":
                    text = args[2]
                    if o_file.name != args[1]:  # if file not opened
                        o_file,str = self.file_mgr.open_file(args[1], 'w')

                    output = o_file.write_to_file(text, self.mem_mgr)

                    if output == None:
                        output = f"{o_file.name} was written"

                elif inp == "close_file":
                    fname = args[1]
                    if o_file != None:
                        o_file = None
                        output = self.file_mgr.close_file(fname)
                    else:
                        # print("No file open")
                        output = "No file open"

                elif inp == "read_file":
                    if o_file != None:
                        output = o_file.read_file(self.mem_mgr)
                        # print(string)
                    else:
                        # print("No file open")
                        output = "No file open"

                elif inp == "truncate_file":
                    # print(f"Current file is {o_file.name}")
                    size = int(args[1])
                    output = o_file.truncate_file(size, self.mem_mgr)

                elif inp == "write_at_file":
                    if o_file.name != args[1]:  # if file not opened
                        o_file,str = self.file_mgr.open_file(args[1], 'w')
                    # print(f"Current file is {o_file.name}")
                    position = int(args[1])
                    size = int(args[2])
                    text = args[3]
                    output = o_file.write_at_file(position, size, text, self.mem_mgr)

                elif inp == "read_file_from":
                    # print(f"Current file is {o_file.name}")
                    position = int(args[1])
                    size = int(args[2])
                    output = o_file.read_file_from(position, size, self.mem_mgr)

                elif inp == "memory_map":
                    output = self.mem_mgr.memory_map()

                # elif inp == "memory":
                #     print(self.mem_mgr.memory)

                # elif inp == "tree":
                #     self.file_mgr.print_tree()

                else:
                    # print("Invalid command")
                    output = "Invalid command"
                
                fd.write(f"\n{output} -> {time.ctime(time.time())}\n")

        fd.close()


    def thread_parser(self, file):
        commands = []
        with open(file) as file:
            commands = [commands.rstrip() for commands in file]
            file.close()
            return commands
