from File_Manager import File_Manager as FM, File, Root, Directory
from Memory_manager import Block, Memory
from treelib import Node, Tree
import math
import os
import json
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

from user import thread_parser

file_mgr = FM(Root())
mem_mgr = Memory()
inp = None
string = None
command = []

command = thread_parser("input_thread1.txt")
inp = command[0] # function name 


load = input('Do you want to load memory? (y/n): ')

if load == 'y':
    file_mgr.root_obj.LoadTree("tree.txt")
    mem_mgr.LoadMem("mem.txt")
    file_mgr.get_files(mem_mgr)

while inp != "q":
    inp = input("Enter command (Write Help for usage details): ")
    # os.system('cls' if os.name == 'nt' else 'clear')
    if inp == "make directory":
        string = input("Enter directory name: ")
        file_mgr.make_directory(string)
    elif inp == "change directory":
        string = input("Enter directory name: ")
        file_mgr.change_dir(string)
    elif inp == "delete directory":
        string = input("Enter directory name: ")
        for key, value  in file_mgr.cwd.files_dict.items():
            o_file = file_mgr.open_file(key, 'w')
            o_file.truncate_file(o_file.size, mem_mgr)
        file_mgr.change_dir(string)
        file_mgr.delete_dir(string)
    elif inp == "create":
        string = input("Enter file name: ")
        file_mgr.create_file(string)
    elif inp == "read":
        print(o_file.read_file(mem_mgr))
    elif inp == "delete file":
        string = input("Enter file name: ")
        o_file = file_mgr.open_file(string, 'w')
        o_file.truncate_file(o_file.size, mem_mgr)
        file_mgr.delete_file(string)
    elif inp == "move file":
        string = input("Enter file name: ")
        src_dir = input("Enter source dir: ")
        dest_dir = input("Enter destination dir: ")
        file_mgr.move_file(src_dir, dest_dir, string)
    elif inp == "open file":
        string = input("Enter file name: ")
        mode = input("Enter the mode: ")
        o_file = file_mgr.open_file(string, mode)
    elif inp == "write":
        text = input("Enter text: ")
        o_file.write_to_file(text, mem_mgr)

    elif inp == "close file":
        string = input("Enter file name: ")
        if o_file != None:
            o_file = None
            file_mgr.close_file(string)
        else:
            print("No file open")
    elif inp == "read file":
        if o_file != None:
            string = o_file.read_file(mem_mgr)
            print(string)
        else:
            print("No file open")
    elif inp == "Truncate":
        print(f"Current file is {o_file.name}")
        size = int(input("Enter the amount to truncate"))
        o_file.truncate_file(size, mem_mgr)
    elif inp == "write@":
        print(f"Current file is {o_file.name}")
        text = input("Enter text: ")
        position = int(input("Enter position: "))
        size = int(input("Enter size: "))
        o_file.write_at_file(position, size, text, mem_mgr)
    elif inp == "read@":
        print(f"Current file is {o_file.name}")
        position = int(input("Enter position: "))
        size = int(input("Enter size: "))
        print(o_file.read_file_from(position, size, mem_mgr))
    elif inp == "map":
        mem_mgr.memory_map()
    elif inp == "mem":
        print(mem_mgr.memory)
    elif inp == "tree":
        file_mgr.print_tree()
    elif inp == "q":
        print("Exiting")
    elif inp == "Help":
        print("map: Shows the memory map")
        print("tree: Shows the file tree")
        print("make directory: Makes a directory")
        print("change directory: Changes directory")
        print("delete directory: Deletes a directory")
        print("create: Creates a file")
        print("delete file: Deletes a file")
        print("move file: Moves a file")
        print("open file: Opens a file")
        print("close file: Closes a file")
        print("read file: Reads a file")
        print("Deallocate Memory: Deallocates memory")
        print("Get Value: Gets the value of a file")
        print("Truncate: Truncates a file")
        print("write@: Writes to a file at a specific position")
        print("read@: Reads a file at a specific position")
        print("write: Writes to a file")
        print("read: Reads a file")
        print("delete: Deletes a file")
        print("Help: Shows this menu")
        print("q: Quits")
    else:
        print("Invalid command")

if file_mgr.root_obj != None:
    mem_mgr.SaveMem('mem.txt')
    file_mgr.root_obj.SaveTree("tree.txt", file_mgr.root_obj.tree)
    file_mgr.filesys_to_json()
    mem_mgr.memory_to_json()
