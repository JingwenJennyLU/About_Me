'''
MACS 30122: Markov models and hash tables
Jingwen Lu
'''

TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hashtable:

    def __init__(self, cells, defval):
        '''
        Construct a new hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted

        Inputs:
            cells (int): initial number of cells of the hashtable (greater than 0)
            default value: value to represent an empty cell in the hashtable

        Returns (none)
        '''
        
        self.size = cells
        self.arr = [(None, defval, None) for _ in range(self.size)]
        self.defval = defval
        self.occupy = 0


    def __custom_hash(self, key):
        '''
        private hash function that takes in a string and returns a hash value. 
        Inputs: key: a string
        returns: a hash value

        '''
        hash = 0
        for char in key:
            hash = (hash * 37 + ord(char)) % self.size
        return hash


    def __getitem__(self, key):
        '''
        Similiar to the __getitem__ method for a Python dictionary, this function
        retrieves the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.

        Inputs:
            key (str): specified key in the hash table
        
        Returns: Associated value, or the default value if key does not exist
        '''

        item = self.__custom_hash(key)
        item_init = item
        while True:
            if self.arr[item][2] is None:
                break
            if self.arr[item][2] and (self.arr[item][0] == key):
                return self.arr[item][1]
            else:
                item += 1
                if item >= self.size:
                    item = 0
                if item == item_init:
                    break
        return self.defval
    

    def __setitem__(self, key, value):
        '''
        Similiar to the __setitem__ method for a Python dictionary, this function
        will change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table, insert it with value "val".

        Inputs:
            key (str): a key
            value: associated value
        
        Returns (none)
        '''
        
        item = self.__custom_hash(key)

        while True:
            if self.arr[item][2] is None:
                self.arr[item] = (key, value, True)
                self.occupy += 1
                break
            elif self.arr[item][0] == key:
                self.arr[item] = (key, value, True)
                break
            else:
                item = (item + 1) % self.size

        #rehash
        if (self.occupy / self.size) > TOO_FULL:
            self.size *= GROWTH_RATIO
            old_arr = self.arr
            self.arr = [(None, self.defval, None) for _ in range(self.size)]
            self.occupy = 0
            for tup in old_arr:
                if tup[2] is True:
                    self.__setitem__(tup[0],tup[1])
               

    def __delitem__(self, key):
        '''
        Similiar to the __delitem__ method for a Python dictionary, this will
        "remove" the key-value pairing inside the hash table. Remember this function
        will not actually remove the key-value pairing from the table but "mark" for
        removal during a rehashing.

        If the key is not found inside the table, you must raise the following error:
             raise RuntimeError("Key was not found in table")

        Inputs:
            key (str): a key
        
        Returns: does not return anything if key exists in table, else raise an error
        '''
        
        item = self.__custom_hash(key)
        item_init = item

        while True:
            if self.arr[item][2] is None:
                raise RuntimeError("Key was not found in table")
            elif (self.arr[item][0] == key) and (self.arr[item][2] is True):
                self.arr[item] = (key, self.arr[item][1], False)
                break
            else:
                item = (item + 1) % self.size
                if item == item_init:
                    raise RuntimeError("Key was not found in table")


    def __contains__(self, key):
        '''
        Similiar to the __contains__ method for a Python dictionary, this will
        return true if the key is inside the hash table; if not it returns false.

        Inputs:
            key (str): a key
        
        Returns (bool): True if key is in hashtable, else False
        '''
        
        item = self.__custom_hash(key)
        item_init = item
        while True:
            if self.arr[item][2] is None:
                return False
            if self.arr[item][2] and (self.arr[item][0] == key):
                return True
            else:
                item += 1
                if item >= self.size:
                    item = 0
                if item == item_init:
                    return False

        
    def keys(self):
        '''
        Returns a list with all the keys inside the hashtable.
        '''
        key_lst = []
        for tup in self.arr:
            if tup[2] is True:
                key_lst.append(tup[0])
        return key_lst


    def values(self):
        '''
        Returns a list with all the values inside the map.
        '''
        val_lst = []
        for tup in self.arr:
            if tup[2] is True:
                val_lst.append(tup[1])
        return val_lst


    def __len__(self):
        '''
           Returns the number key-value pairings inside the hashtable.
        '''
        count = 0
        for tup in self.arr:
            if tup[2] is True:
                count += 1
        return count