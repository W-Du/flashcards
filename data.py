class GuestWord:
    def __init__(self, word, description = None):
        self.word = word
        self.description = description
        self.lists = set()
        self.priority = 7
    
    def setDescription(self, description):
        self.description = description
    
    def addToList(self, lst):
        if not isinstance(lst, GuestList):
            raise Exception('a GuestList object expected in addToList()')
        self.lists.add(lst)
        lst.words.append(self)

    def removeFromList(self, lst):
        if not isinstance(lst, GuestList):
            raise Exception('a GuestList object expected in removeFromList()')
        self.lists = [l for l in self.lists if l.listname != lst.listname]
        # lst.words = [w for w in lst.words if w.word != self.word]

    def getLists(self):
        return self.lists

    def pIncrease(self):
        self.priority += 1

    def pDecrease(self):
        self.priority -= 1

    # def __repr__(self):
    #     return self.word + '\n' + self.description

    def __repr__(self):
        return self.word


class GuestList:
    def __init__(self, listname):
        self.listname = listname
        self.words = []
        self.id = 0

    def addWord(self, word):
        if not isinstance(word, GuestWord):
            raise Exception("a GuestWord object expected in addWords()")        
        if word not in self.words:
            self.words.append(word)
        if self not in word.lists:
            word.lists.add(self)
            
    def removeWord(self, word):
        if not isinstance(word, GuestWord):
            raise Exception('a GuestWord object expected in removeWord()')
        else:
            self.words = [w for w in self.words if w.word != word.word] 
            return word   

    def setId(self, id):
        self.id = id

    def getWord(self, word):
        for w in self.words:
            if w.word == word:
                return w

    def __str__(self):
        return 'list id: {}; list name: {}; contains {} words \n'.format(self.id, self.listname, len(self.words))   


class Guest:
    def __init__(self):
        self.username = 'Guest'
        self.lists = []
        self.words = []
    
    def addList(self, lst):
        if not isinstance(lst, GuestList):
            raise Exception('object of Guestlist is expect from addList()')
        for l in self.lists:
            if lst.listname == l.listname:
                raise Exception(f'a list with listname of {lst.listname} already exists')
                return
        if len(self.lists) > 0:
            lastLst = self.lists[len(self.lists) -1]
            lst.setId(lastLst.id + 1)
        self.lists.append(lst)

    def removeList(self, lst):
        if not isinstance(lst, GuestList):
            raise Exception('object of Guestlist is expect from removeList()')
        else:
            self.lists = [l for l in self.lists if l.listname != lst.listname]

    def getListByName(self, listname):
        for l in self.lists:
            if l.listname == listname:
                return l
        return None
    
    def getListById(self, id):
        for l in self.lists:
            if l.id == id:
                return l
        return None

    def updateWords(self):
        wordSet=set()
        for lst in self.lists:
            wordSet.update(lst.words)
        # self.words = list(wordSet)
        self.words = arrangeByFirstLetter(list(wordSet))

    def getWord(self, word):
        for w in self.words:
            if w.word == word:
                return w
        return None
            
def arrangeByPriority(lst): # a list of GuestWord objects
    res = sorted(lst, key=prio, reverse=True)
    return res

def arrangeByFirstLetter(lst): 
    res = sorted(lst, key=firstLetter)
    return res

def prio(elem):
    return elem.priority

def firstLetter(elem):
    return elem.word[0]





# pre-defined data
word1 = GuestWord('anomaly', 'noun - something that is unusual or unexpected; The student\'s poor performance on the latest test was an anomaly since she had previously earned excellent grades.')
word2 = GuestWord('equivocal', 'adj. – not easily understood or explained')
word3 = GuestWord('lucid', 'adj. – very clear and easy to understand')
word4 = GuestWord('assuage', 'verb – to make (an unpleasant feeling) less intense')
word5 = GuestWord('erudite', 'adj. – having or showing great knowledge')
word6 = GuestWord('prodigal', 'adj. – wastefully extravagant')
word7 = GuestWord('enigma', 'noun – a person or thing that is mysterious, puzzling, or difficult to understand')
word8 = GuestWord('fervid', ' adj. – intensely enthusiastic or passionate')
word9 = GuestWord('abstain', 'verb – to restrain oneself for doing or enjoying something')
word10 = GuestWord('audacious', 'adj. – a willingness to take bold risks / adj. –  showing a lack of respect')
word11 = GuestWord('desiccate', 'verb – remove the moisture from (something)')
word12 = GuestWord('gullible', 'adj. – easily persuaded to believe something')

list1 = GuestList('default')
for word in [word1, word2, word3, word4, word5, word6, word7, word8, word9, word10, word11, word12]:
    list1.addWord(word)


# guest to be exported
guestData = Guest()
guestData.addList(list1)
# print(list1.id)
guestData.updateWords()
# word1.priority -= 2
# word2.priority -= 1
# word3.priority += 1
# guestData.updateWords()

# print(guestData.words)




