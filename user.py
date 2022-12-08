from File_Manager import File_Manager as FM, File, Root, Directory
from Memory_manager import Block, Memory
from treelib import Node, Tree

def thread_parser(file):
    # read file
    commands = []
    args = []
    with open(file) as file:
        commands = [commands.rstrip() for commands in file]
        print(commands)

    for command in commands:
       args = command.split(" ")
       print(args)
       return args



        
       