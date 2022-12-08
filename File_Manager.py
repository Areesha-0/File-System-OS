from treelib import Node, Tree
import math
import json
from Memory_manager import Block, Memory
import pickle


class Root():
    def __init__(self):
        self.tree = Tree()  # creating tree
        self.name = "Root"
        self.tree.create_node(self.name, self.name)  # creating root node

    def to_dict_(self, nid=None, key=None, sort=False, reverse=False, with_data=False):
        """Transform the whole tree into a dict."""

        nid = self.tree.root if (nid is None) else nid
        ntag = self.tree[nid].tag
        tree_dict = {ntag: {"children": []}}
        if with_data:
            if self.tree[nid].data is not None:
                # converting directory objects to dict
                tree_dict[ntag]["data"] = self.tree[nid].data.__dict__
#                 print(tree_dict[ntag]["data"])
                file_dict = tree_dict[ntag]["data"]['files_dict']
                for key, value in file_dict.items():
                    # converting file objects to dict
                    file_dict[key] = value.__dict__
                    if value.mem_locations:
                        for i in range(len(value.mem_locations)):
                            # print(value.mem_locations[i])
                            # converting block objects to dict
                            value.mem_locations[i] = value.mem_locations[i].__dict__
            else:
                tree_dict[ntag]["data"] = self.tree[nid].data

        if self.tree[nid].expanded:
            queue = [self.tree[i] for i in self.tree[nid].fpointer]
            key = (lambda x: x) if (key is None) else key
#             if sort:
#                 queue.sort(key=key, reverse=reverse)

            for elem in queue:
                print(tree_dict[ntag]["children"].append(
                    self.to_dict_(elem.identifier, with_data=with_data, sort=sort, reverse=reverse)))

            if len(tree_dict[ntag]["children"]) == 0:
                tree_dict = self.tree[nid].tag if not with_data else \
                    {ntag: {"data": self.tree[nid].data.__dict__}}
            return tree_dict

    def SaveTree(self, savepath_pickle, tree_dict):
        with open(savepath_pickle, "wb") as file:
            pickle.dump(tree_dict, file)

    def LoadTree(self, loadpath_pickle):
        with open(loadpath_pickle, 'rb') as file:
            self.tree = pickle.load(file)


class Directory():
    def __init__(self, name):
        self.path = "Root/" + name
        self.name = name
        self.files_dict = dict()

class File:

    def __init__(self, name):
        self.name = name
        self.mem_locations = list()  # list of block objects
        self.size = 0
        self.mode = 'r'  # if not specified then only in read mode

    def isin_memory(self):
        if len(self.mem_locations) != 0:  # file in memory
            return self.mem_locations[-1]  # return last block
        return None

    def num_blocks(self, txt_len, b_size):
        return math.ceil(txt_len / b_size)

    def text_to_chunks(self, text, b_size):
        length = len(text)
        l = list()
        l.append(text)

        if length > b_size:
            return [text[i:i+b_size] for i in range(0, len(text), b_size)]
        else:
            return l

    def read_file(self, mem_obj):
        # if self.mode == 'r':
        data = ""
        for block in self.mem_locations:
            data = data + mem_obj.get_value(block)

        return data

        # else: print("File is not open in read mode")

    def write_to_file(self, text, mem_obj):
        if self.mode == 'w':
            isin_mem = self.isin_memory()
            space_req = 0
            b_size = 20
            blocks = {}
            txt_len = len(text)

             #file doesnt exist in memory then just get num blocks from memory
            if isin_mem == None or isin_mem.b_occupied == isin_mem.size :
                space_req = self.num_blocks(txt_len, b_size)
                blocks = mem_obj.get_block(space_req)  #get blocks from memory

                if blocks != None:
                    txt_chunks = self.text_to_chunks(text, b_size)

                    for index, block in enumerate(blocks):
                        b = mem_obj.write_to_block(block,txt_chunks[index], self.name)
                        self.mem_locations.append(b)

                        if len(txt_chunks) == index+1: break
                else: 
                    # print("Cannot write to file, no more space!")
                    return "Cannot write to file, no more space!"

            else: # check how many to accomodate in last block
                remaining = txt_len - (isin_mem.size - isin_mem.b_occupied)
                accomodated = txt_len - remaining # block will accomodate

                b = mem_obj.write_to_block(isin_mem,mem_obj.memory[isin_mem]+text[:accomodated] ,self.name)

                if remaining != 0 and remaining > 0:
                    # for remaining get num_blocks by reducing length of text
                    space_req = self.num_blocks(remaining, b_size)
                    blocks = mem_obj.get_block(space_req)

                    if blocks != None:
                        txt_chunks = self.text_to_chunks(text[accomodated:], b_size)

                        for index, block in enumerate(blocks):
                            b = mem_obj.write_to_block(block,txt_chunks[index], self.name)
                            self.mem_locations.append(b)

                            if len(txt_chunks) == index+1: break
                    
                        return "Written to file"
                    else: 
                        # print("Cannot write to file, no more space!")
                        return "Cannot write to file, no more space!"

            self.update_fsize(mem_obj)
            
        else: 
            # print("File is not open in write mode!")
            return "File is not open in write mode!"

    def remove_mem(self):
        self.mem_locations.clear()

    def write_at_file(self, write_at, size, text, mem_obj):
        if self.mode == 'w':
            if self.isin_memory() != None:
                data = self.read_file(mem_obj)
                tobe_replaced = data[write_at:size+write_at]
                data = data.replace(tobe_replaced, text)

                mem_obj.deallocate_mem(self.name)
                self.remove_mem()
                self.write_to_file(data, mem_obj)
                self.update_fsize(mem_obj)

                return f"File was written at {write_at}"
        else:
            # print("File is not open in write mode!")
            return "File is not open in write mode!"

    def read_file_from(self, start, size, mem_obj):
        if self.mode == 'r' and size <= self.size and size > 0:
            data = self.read_file(mem_obj)

            # print(f'data: {data[start:start+size]}')
            return f'data: {data[start:start+size]}'
        else:
            # print("Error! File is not open in read mode or size is invalid!")
            return "Error! File is not open in read mode or size is invalid!"

    def move_content(self, start_index, target_index, size, mem_obj):
        if self.mode == 'w':

            data = self.read_file(mem_obj)

            # extract data to be moved
            tobe_moved = data[start_index:size+start_index]
            data = data.replace(tobe_moved, "")  # removing data from there

            target_index = target_index - size
            s1 = data[:target_index]
            s2 = data[target_index:]
            data = s1 + tobe_moved + s2
            mem_obj.deallocate_mem(self.name)
            self.remove_mem()
            self.write_to_file(data, mem_obj)

            return "File's content is moved!"

        else:
            # print("File is not open in write mode!")
            return "File is not open in write mode!"

    def truncate_file(self, size, mem_obj):
        if self.mode == 'w':

            data = self.read_file(mem_obj)
            data = data[:size]
            mem_obj.deallocate_mem(self.name)
            self.remove_mem()
            # print(f"clear {self.mem_locations}")
            self.write_to_file(data, mem_obj)
            self.update_fsize(mem_obj)

            if self.size == size:
                mem_obj.deallocate_mem(self.name)
                self.remove_mem()
                self.update_fsize(mem_obj)
            
            return "File truncated sucessfully!"

        else:
            # print("File is not open in write mode!")
            return "File is not open in write mode!"

    def update_fsize(self, mem_obj):
        self.size = len(self.read_file(mem_obj))
        for i in self.mem_locations:
            i.fsize = self.size

    def update_memlocations(self, mem_obj):
        self.mem_locations.clear()

        for key, value in mem_obj.memory.items():
            if key.f_name == self.name:
                self.mem_locations.append(key)


class File_Manager:
    def __init__(self, root_obj):
        self.root_obj = root_obj
        self.cwd = root_obj

    def print_tree(self):
        self.root_obj.tree.show()

    def make_directory(self, name):
        parent = None
        if self.cwd == self.root_obj:  # if directory orignates from root
            parent = self.root_obj.name

        elif hasattr(self.cwd, 'files_dict') == True:  # if sub directory
            parent = self.cwd.name

        else:
            # print("Directory cannot be created from this location")
            return "Directory cannot be created from this location"

        if self.root_obj.tree.get_node(name) != None:
            # print('Directory already exists')
            return 'Directory already exists'

        else:
            dir_ = Directory(name)
            node = Node(dir_.name, dir_.name, data=dir_)
            new_dir = self.root_obj.tree.add_node(node, parent=parent)  # adding node to tree
            self.cwd = node.data  # pointing cwd to the directory formed
            # print(f"Diretory created: {name}")
            return f"Diretory created: {name}"


    def delete_dir(self, name):
        if hasattr(self.cwd, 'files_dict') == True:
            # if name in self.cwd.files_dict:
                # self.root_obj.tree.remove_node(self.cwd.files_dict[name].name)
                self.root_obj.tree.remove_node(name)
                del self.cwd.files_dict
                # print(f"Diretory deleted: {name}")
                return f"Diretory deleted: {name}"
            # else:
            #     print("Directory does not exist")
        else:
            # print("Directory cannot be deleted from this location")
            return "Directory cannot be deleted from this location"

    def change_dir(self, goto_dir):
        if goto_dir == self.cwd.name:  # already in the current diectory
            # print("You are in the same directory")
            return "You are in the same directory"

        elif goto_dir == "Root":  # root is also a directory
            self.cwd = self.root_obj

        else:
            self.cwd = self.root_obj
            dir_node = self.cwd.tree.get_node(goto_dir)  # get directory node from root

            if dir_node == None:
                # print("This directory does not exist")
                return "This directory does not exist"
            else:
                self.cwd = dir_node.data  # set ptr to changed dir
                # print(f"You are now at {self.cwd.name}")
                return f"You are now at {self.cwd.name}"

    def create_file(self, fname):
        if hasattr(self.cwd, 'files_dict') == True:  # if cwd points to a directory
            # cannot have files with same name
            if self.cwd.files_dict.get(fname) == None:
                dir_ = self.cwd
                # creating file inside dir's dictionary of files
                dir_.files_dict.update({fname: File(fname)})
                self.cwd = dir_
                # print(f"File created: {fname}")
                return f"File created: {fname}"
            else:
                # print('A file with this name already exists. Please choose another name')
                return 'A file with this name already exists. Please choose another name'

        else:
            # print("Cannot create file from this location")
            return "Cannot create file from this location"

    def delete_file(self, fname):
        if hasattr(self.cwd, 'files_dict') == True:  # if cwd points to a directory
            dir_ = self.cwd

            if fname in dir_.files_dict:  # file exists in that directory
                # deleting file inside dir's dictionary of files
                dir_.files_dict.pop(fname)
                # print(f"File created: {fname}")
                return f"File created: {fname}"

            else:
                # print("File does not exist in this directory")
                return "File does not exist in this directory"

        else:
            # print("Cannot delete file from this location")
            return "Cannot delete file from this location"

    def move_file(self, src_dir, dest_dir, src_file):
        if src_dir == dest_dir:  # already in destination dir
            # print("File is in the same directory already")
            return "File is in the same directory already"
        else:
            self.change_dir(src_dir)  # go to source dir and cut the file obj
            file_obj = self.cwd.files_dict[src_file]  # save file obj
            self.delete_file(src_file)  # deleting file from src dir

            self.change_dir(dest_dir)  # going to destination dir
            # adding file obj to that dir
            self.cwd.files_dict.update({src_file: file_obj})
            # print(f"File moved from {src_dir} to {dest_dir}")
            return f"File moved from {src_dir} to {dest_dir}"

    def open_file(self, fname, mode):
        self.cwd.files_dict[fname].mode = mode
        # print(f"File opened: {fname} in {mode} mode")
        return self.cwd.files_dict[fname], f"File opened: {fname} in {mode} mode"  # return file object t

    def close_file(self, fname):
        # print(f'You are at {self.cwd.name}. The file was closed!')
        return f'You are at {self.cwd.name}. The file was closed!'

    def filesys_to_json(self):
        tree_dict = self.root_obj.to_dict_(with_data=True)

        # Serializing json
        json_object = json.dumps(tree_dict, indent=2)

        # Writing to sample.json
        with open("file_structure.json", "w") as outfile:
            outfile.write(json_object)

    def get_files(self, mem):
        for node in self.root_obj.tree.all_nodes_itr():
            if hasattr(node.data, 'files_dict') == True:
                files = node.data.files_dict
                for key, value in files.items():
                    value.update_memlocations(mem)

