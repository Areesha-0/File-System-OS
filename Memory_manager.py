
import json
import pickle

class Block:
    def __init__(self, name, is_full=0, f_name=None, size=20, b_occupied=0,fsize=0):
        self.name = name
        self.is_full = is_full # 0 if block is not full, 1 if block is full
        self.f_name = f_name
        self.size = size #20 string characters  
        self.b_occupied = b_occupied
        self.fsize = fsize


class Memory:
    def __init__(self):
        self.memory = dict()
        self.size = 10 # accomodates 10 blocks
        self.occupied = 0
        
        # initializing memory
        for i in range(self.size):
            self.memory[Block(f'block {i + 1}')] = ''     
            
        
    def get_block(self, num_blocks):
        blocks = {}
        i = 0
        for block, data in self.memory.items():
            # find empty blocks and write to it 
            if block.b_occupied != block.size and block.f_name == None: # empty blocks returned only
                blocks[block] = data
                i = i + 1
                if i == num_blocks: break
                    
        if not bool(blocks):
            print("Memory is full, no more blocks found!")
            return None
                
        return blocks
    
    
    def write_to_block(self, block_obj, text, f_name):
        if self.memory.get(block_obj) != None:
            block_obj.f_name = f_name
            block_obj.b_occupied = len(text)

            if block_obj.b_occupied == block_obj.size:
                block_obj.is_full = 1
                
            self.memory[block_obj] = text

        return block_obj
    
    def get_value(self, block_obj):
        return self.memory[block_obj]
            
    def deallocate_mem(self,fname):
        for block, data in self.memory.items():
            if block.f_name == fname:
                self.memory[block] = '' 
                block.f_name = None
                block.b_occupied = 0
                block.is_full = 0
                block.fsize=0
                
    def memory_map(self):
        for block, data in self.memory.items():
            print(f"{block.name}: File: {block.f_name} of size {block.fsize}")

    def memory_to_json(self):
        mem = self.memory
        mem_json = dict()
        for key, value in mem.items():
            new_key = key.__dict__
            if value == "": value = None
            mem_json[key.name] = [new_key, value] #list with first block object and then value
            
        #Serializing json
        json_object = json.dumps(mem_json, indent=2)
 
        # Writing to sample.json
        with open("memory.json", "w") as outfile:
            outfile.write(json_object)

    def SaveMem(self, savepath_pickle):
        with open(savepath_pickle, "wb") as file:
            pickle.dump(self.memory, file)

    def LoadMem(self, loadpath_pickle):
        with open(loadpath_pickle, 'rb') as file:
            self.memory = pickle.load(file)



