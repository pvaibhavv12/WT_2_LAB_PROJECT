# from PredictionTree import *
import pandas as pd
import copy
import random
import sqlite3

class PredictionTree():
    Item = None
    Parent = None
    Children = None
    
    def __init__(self,itemValue=None):
        self.Item = itemValue
        self.Children = []
        self.Parent = None
        
    def addChild(self, child):
        newchild = PredictionTree(child)
        newchild.Parent = self
        self.Children.append(newchild)
        
    def getChild(self,target):
        for chld in self.Children:
            if chld.Item == target:
                return chld
        return None
    
    def getChildren(self):
        return self.Children
        
    def hasChild(self,target):
        found = self.getChild(target)
        if found is not None:
            return True
        else:
            return False
        
    def removeChild(self,child):
        for chld in self.Children:
            if chld.Item==child:
                self.Children.remove(chld)


class CPT():

    alphabet = None # A set of all unique items in the entire data file
    root = None # Root node of the Prediction Tree
    II = None #Inverted Index dictionary, where key : unique item, value : set of sequences containing this item
    LT = None # A Lookup table dictionary, where key : id of a sequence(row), value: leaf node of a Prediction Tree

    def __init__(self):
        self.alphabet = set()
        self.root = PredictionTree()
        self.II = {}
        self.LT = {}

    def load_files(self,train_file,test_file = None):

        """
        This function reads in the wide csv file of sequences separated by commas and returns a list of list of those
        sequences. The sequences are defined as below.

        seq1 = A,B,C,D
        seq2  B,C,E

        Returns: [[A,B,C,D],[B,C,E]]


        """
        
        data = [] # List of list containing the entire sequence data using which the model will be trained.
        target = [] # List of list containing the test sequences whose next n items are to be predicted
        
        if train_file is None:
            return train_file
        
        train = pd.read_csv(train_file)
    
        for index, row in train.iterrows():
            data.append(row.values)
            
        if test_file is not None:
            
            test = pd.read_csv(test_file)
            
            for index, row in test.iterrows():
                data.append(row.values)
                target.append(list(row.values))
                
            return data, target
        
        return data
        


    # In[3]:


    def train(self, data):

        """
        This functions populates the Prediction Tree, Inverted Index and LookUp Table for the algorithm.

        Input: The list of list training data
        Output : Boolean True

        """
        
        cursornode = self.root
        

        for seqid,row in enumerate(data):
            for element in row:

                # adding to the Prediction Tree

                if cursornode.hasChild(element)== False:
                    cursornode.addChild(element)
                    cursornode = cursornode.getChild(element)

                else:
                    cursornode = cursornode.getChild(element)

                # Adding to the Inverted Index

                if self.II.get(element) is None:
                    self.II[element] = set()

                self.II[element].add(seqid)
                
                self.alphabet.add(element)

            self.LT[seqid] = cursornode

            cursornode = self.root
            
        return True


    def score(self, counttable,key, length, target_size, number_of_similar_sequences, number_items_counttable):


        """
        This function is the main workhorse and calculates the score to be populated against an item. Items are predicted
        using this score.

        Output: Returns a counttable dictionary which stores the score against items. This counttable is specific for a 
        particular row or a sequence and therefore re-calculated at each prediction.


        """



        weight_level = 1/number_of_similar_sequences
        weight_distance = 1/number_items_counttable
        score = 1 + weight_level + weight_distance* 0.001
        
        if counttable.get(key) is None:
            counttable[key] = score
        else:
            counttable[key] = score * counttable.get(key)
            
        return counttable



    def predict(self,data,target,k, n=1): 
        """
        Here target is the test dataset in the form of list of list,
        k is the number of last elements that will be used to find similar sequences and,
        n is the number of predictions required.

        Input: training list of list, target list of list, k,n

        Output: max n predictions for each sequence
        """
        
        predictions = []
        
        for each_target in target:
            each_target = each_target[-k:]
            
            intersection = set(range(0,len(data)))
            
            for element in each_target:
                if self.II.get(element) is None:
                    continue
                intersection = intersection & self.II.get(element)
            
            similar_sequences = []
            
            for element in intersection:
                currentnode = self.LT.get(element)
                tmp = []
                while currentnode.Item is not None:
                    tmp.append(currentnode.Item)
                    currentnode = currentnode.Parent
                similar_sequences.append(tmp)
                
            for sequence in similar_sequences:
                sequence.reverse()
                
            counttable = {}

            for  sequence in similar_sequences:
                try:
                    index = next(i for i,v in zip(range(len(sequence)-1, 0, -1), reversed(sequence)) if v == each_target[-1])
                except:
                    index = None
                if index is not None:
                    count = 1
                    for element in sequence[index+1:]:
                        if element in each_target:
                            continue
                            
                        counttable = self.score(counttable,element,len(each_target),len(each_target),len(similar_sequences),count)
                        count+=1


            pred = self.get_n_largest(counttable,n)
            predictions.append(pred)

        return predictions



    def get_n_largest(self,dictionary,n):


        """
        A small utility to obtain top n keys of a Dictionary based on their values.

        """
        largest = sorted(dictionary.items(), key = lambda t: t[1], reverse=True)[:n]
        return [key for key,_ in largest]



model = CPT()

# data = [[11,12,13,21,22,23],[22,23,11,12],[31,32,33,21,22,23],[11,22,23]]
# data = [['array1','array2','array3'],['array1','array2','array2','array1']]


'''
data = [['array1','array2','matrix1','matrix2','string1'],
['array2','array1','Heap2','Heap2','HashTable3','string1','stack2'],
['array2','array1','string2','Heap2','matrix2','matrix1'],
['HashTable2','array1','matrix1','string1','stack1','string1','queue1','HashTable3'],
['matrix1','matrix2','queue1','Heap2','Heap3','queue2','stack2','stack1'],
['string1','Heap2','HashTable2','stack1','stack2','stack3','queue1','queue2','string2'],
['matrix1','stack1','stack2','queue1','queue3','Heap2','Heap3'],
['stack1','stack2','array1','array3','queue3','stack1','string1','string3'],
['queue2','queue1','Heap2','Heap3','queue2','stack1','string1'],
['Heap1','matrix1','matrix2','queue1','HashTable3'],
['array1','Heap1','matrix1','matrix2','string1']]
'''
def get_prediction(seq):
    difficulty = seq[-1]
    datastructure = seq[:len(seq) - 1]
    target = seq
    model.train(data)
    predictions = model.predict(data,target,5,2)
    return predictions

fp = open("prediction_train.txt")
td = fp.read().strip()
fp.close()
td =td.split("\n")
data=[]

for row in td:
    datapoints = row.split(",")
    temp_list=[]
    for a in datapoints:
        temp_list.append(a)
    temp_list1=copy.deepcopy(temp_list)    
    data.append(temp_list1)

to_print=""

inp_string = input()
if(inp_string==""):
    to_print = "string1,array1"
    
#inp_string ="array1,array2"
else:
    l_p = [[]]
    inp_string =inp_string.split(sep=",")

    last_question = inp_string[-1]
    last_type=last_question[0:len(last_question)-1]
    last_level=last_question[-1]

    for i in inp_string:
        l_p[0].append(i)

    predicted = get_prediction(l_p)

    out_str = ""

    p_ques = len(predicted[0])

    for i in predicted[0]:
        out_str=out_str+i+","


    for i in range(2-p_ques):
        temp=['array','matrix','queue','heap','stack','string','HashTable']
        
        temp.remove(last_type)
        to_add = random.choice(temp)
        to_add=to_add+last_level
        out_str=out_str+to_add+","

    out_str=out_str.rstrip(",")

    to_print = out_str


connection = sqlite3.connect("users.db")
final_output=""

final_output_type=""

for ii in (to_print.split(sep=",")):
    i=ii[0:(len(ii)-1)]
    
    res = connection.execute("SELECT name from list_of_questions where type ='" + i +"'")

    temp_list2 = []

    for a in res:
        
        temp_list2.append(a[0])
    
    q = random.choice(temp_list2)
    final_output =final_output + q + ","
    final_output_type =final_output_type + i +","

final_output=final_output.rstrip(",")
final_output_type=final_output_type.rstrip(",")

connection.close()

print(final_output)
print(final_output_type)


