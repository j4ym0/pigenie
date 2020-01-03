







class Average(): # used to collect data and average over time or values

    def __init__(self, size=6):
        self.store_size = (size+1)
        self.store = [0] * self.store_size  # init array of the size + 1 for the average result
        self.store[0] = 0                   # init the average for later
        self.fastinit = True                # 1 = number of values
        self.type = 1                       # 1 = number of values
                                            # 2 = TODO over time

    def add(self, value): # add a result to the array
        del self.store[1] # delete the yongest value
        self.store.append(value) # add the value to the end

        if self.fastinit: # if valuse is 0 then init with current value
            for i in range(len(self.store)-1):
                if self.store[i+1] == 0:
                    self.store[i+1] = value
            self.fastinit = False # turn off so is not called later

        a = 0
        for i in range(len(self.store)-1):
            a += self.store[i+1]

        self.store[0] = a/(len(self.store)-1) # get the avarage from the new result array


    def clear(): # clear all the results and reset
        self.store = [0] * self.store_size # init array of the size + 1 for the average result
        self.store[0] = 0 # init the average for later

    def average(self): # retreve the average
        return self.store[0]
