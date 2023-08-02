class GuestWord:
    def __init__(self, word, description = None):
        self.word = word
        self.description = description
        self.lists = []
        self.priority = 7
    
    def setDescription(self, description):
        self.description = description
    
    def addToList(self, listname):
        self.lists.append(listname)

    def getLists(self):
        return self.lists

    def pIncrease(self):
        self.priority += 1

    def pDecrease(self):
        self.priority -= 1

    def __repr__(self):
        return self.word + '\n' + self.description


class GuestList:
    def __init__(self, listname):
        self.listname = listname
        self.words = []

    def addWords(self, wordsLst):
        for word in wordsLst:
            if not isinstance(word, GuestWord):
                raise Exception('a GuestWord object expected in addWord()')
            if word not in self.words:
                self.words.append(word)
            if self.listname not in word.lists:
                word.lists.append(self.listname)
            
    def removeWord(self, word):
        if not isinstance(word, GuestWord):
            raise Exception('a GuestWord object expected in removeWord()')
        else:
            self.words = [w for w in self.words if w.word != word.word]    
            return word   

    def __repr__(self):
        return 'list name: {}; contains {} words'.format(self.listname, len(self.words))   


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
        self.lists.append(lst)

    def removeList(self, lst):
        if not isinstance(lst, GuestList):
            raise Exception('object of Guestlist is expect from removeList()')
        else:
            self.lists = [l for l in self.lists if l.listname != lst.listname]

    def getList(self, listname):
        for l in self.lists:
            if l.listname == listname:
                return l
        return None

    def updateWords(self):
        for lst in self.lists:
            self.words += lst.words
            




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
list1.addWords([word1, word2, word3, word4, word5, word6, word7, word8, word9, word10, word11, word12])


# guest to be exported
guestData = Guest()
guestData.addList(list1)
guestData.updateWords()

# print(guest.lists[0])
# print(guestData.username)



