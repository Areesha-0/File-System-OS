from File_Manager import File_Manager as FM, File, Root, Directory
from Memory_manager import Block, Memory
from treelib import Node, Tree
import math
import os
import json
from user import User_Thread

file_mgr = FM(Root())
mem_mgr = Memory()
threads = []

load = input('Do you want to load memory? (y/n): ')
if load == 'y':
    file_mgr.root_obj.LoadTree("tree.txt")
    mem_mgr.LoadMem("mem.txt")
    file_mgr.get_files(mem_mgr)

num_threads = int(input("Enter number of threads: "))
th = 0
while th != num_threads:
    # Create new thread
    th = th + 1
    thread = User_Thread(th, "Thread"+str(th), file_mgr, mem_mgr)
    threads.append(thread)

    # Start new Thread
    thread.start()

for thread in threads:
    thread.join()

print("All threads executed. Now in main!")

if file_mgr.root_obj != None:
    mem_mgr.SaveMem('mem.txt')
    file_mgr.root_obj.SaveTree("tree.txt", file_mgr.root_obj.tree)
    file_mgr.filesys_to_json()
    mem_mgr.memory_to_json()
