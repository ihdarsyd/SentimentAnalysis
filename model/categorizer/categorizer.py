from scipy import spatial
from operator import itemgetter
from .category import Category
import itertools
import numpy as np
import pandas as pd
import time
import sys,os
from operator import itemgetter
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

sys.path.append(os.path.abspath(os.path.join('..', 'tweets')))

class Categorizer:
    def __init__(self):
        self.category = Category()
        #Matriks Kategori (Array)
        self.category_m = self.category.generateCategorySpace()
       # np.savetxt('matrik_ketegori.csv', self.category_m, delimiter=',', fmt='%s')
        self.keys = self.category.keys
        self.key_list = []
        self.text = ""
        self.THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(self.THIS_FOLDER, 'stopwords.xlsx')
        self.stopwords_excel = pd.read_excel(self.filename, 'Sheet1')
        self.stopwords = self.stopwords_excel['kata'].values.tolist()

    def getMaxKeys(self, result):
        result = sorted(result, key=itemgetter(2), reverse=False)
        try:
            if result[0][2] < 9:
                return result[0][0]
        except:
            return None
    def deleteSymbol(self, sentence):
       #Menghapus simbol
       symbol = ['”', '$', '%', '&', '’', '(', ')', '*', '+','/', ':', ';', '<', '=', '>', '@', '[', "RT ", ']', '^', '_', '`', '{', '|', '}', '~']
       for i in symbol : 
              sentence = sentence.replace(i, '')   
       return sentence
    
    def numberConverter(self, sentence):
        #Menghapus angka
        number = ['1','2','3','4','5','6','7','8','9','0']
        for i in number : 
                sentence = sentence.replace(i, '')   
        return sentence

    def removeAffixNya(self, sentence): #bkn rule
        # Remove affixes nya except for word harus
        excep= ['harus', 'ha', 'ta']
        return ' '.join([word.replace("nya",'') for word in sentence.split(" ") if word not in excep])

    def removeMentions(self, sentence): #bkn rule
        # Remove account mentions in sentence
        return (' '.join([word for word in sentence.split(" ") if '@' not in word and 'http' not in word]))
   
    def preprocessing(self, sentence):
        sentence = self.removeMentions(str(sentence).lower())
        sentence = self.deleteSymbol(sentence)
        sentence = self.numberConverter(sentence)
        return sentence
    
    def filtering(self, words):
       for word in words:
              if word in self.stopwords:
                     words.remove(word)
       return words

    def stemmingWord(self, word):
       word = stemmer.stem(' '.join(word))
       return word.split(" ")
    
    def hastagrule(self, words):
        hastag_word = []
        for word in words:
            if "#" in word:
                words.extend([x for x in self.keys if x in word])
                words.remove(word)
        # print(words, hastag_word, words.extend(hastag_word))
        return words
        
    def getContentKeys(self, content):
        content = self.preprocessing(content)
        content = list(filter(None, content.split(" ")))
        content = [item for item in content]
        content = self.hastagrule(content)
        content = self.filtering(content)
        content = self.stemmingWord(content)

        # content = self.sanitize(content).split(" ")
        # content = list(filter(None, content))
        words = []
        for word in content:
            result = []
            # for idx,data in enumerate(self.keys):
            #     result.append([self.keys[idx], word, self.characterChecker(data, word)])
            # key = self.getMaxKeys(result)
            # if key is None:
            #     words.append(word)
            # else:
            #     words.append(key)
            if word in self.keys:
                self.key_list.append(word)
            words.append(word)
        self.text = " ".join(words)

        return [key for key in self.key_list if key is not None]

    def getContentCategory(self, content):
        try:
            self.key_list = self.getContentKeys(content)
            result = []
            for idx,item in enumerate(self.category_m):
                result.append([list(self.category.dict_c.keys())[idx], 
                    self.innerProductDistance(item,self.category.generateKeySpace(self.key_list))])
            result = sorted(result, key=itemgetter(1), reverse=True)  
            
            if result[0][1] != 0:
                return [result[0][0], self.key_list]
            else:
                return ['nocategory', self.key_list]
        except:
            return ['nocategory', self.key_list]

    def characterChecker(self, data, query):
        temp = data
        if len(data) < len(query):
            data = query
            query = temp
            
        count = 0
        flag = 0
        tempdiffer = -1
        differ = 0
        tempidx = -1
        target = 0
        for idx, char in enumerate(data):
            found = query.find(char, target)
            target = found if found != -1 else query.find(char) 
                
            if target == -1:
                count += 5
                flag = 0
                continue
            differ = idx - target
            if abs(differ) >= 1:
                count += 3
            if tempdiffer == differ or target >= ((idx-1)-tempdiffer): 
                flag += 1
            else:
                flag = 0
            tempdiffer = differ
            count += abs(differ)
            if flag >= (0.8*len(temp)): return 0
        return count
    
    def innerProductDistance(self, p, q):
        tot = 0
        for idx in np.nonzero(q)[0].tolist():
            tot += (p[idx]*q[idx])
        return tot
    
    def cleanWord(self, word):
        skipindex = []
        result = []
        for i, ch in enumerate(word):
            if i not in skipindex: 
                result.append(ch)
                if ch in ['a', 'i', 'u', 'e', 'o']:
                    try:
                        for j in range(i+1,len(word)):
                            if word[j] == ch:
                                skipindex.append(j)
                            else: break
                    except IndexError:
                        pass
                else:
                    try:
                        if word[i+1] == ch:
                            for j in range(i+2,len(word)):
                                if word[j] == ch:
                                    skipindex.append(j)
                                else: break
                    except IndexError:
                        pass
        return ''.join(result)

    def sanitize(self, sentence):
        cleansentence = []
        sentence = sentence.lower().replace('.','').replace(',','').replace('!','').replace('?','').replace('_','')
        for word in sentence.split(" "):
            word = "".join([x for x in word if not x.isdigit()])
            word = self.cleanWord(word)
            if word not in self.stopwords:
                cleansentence.append(word)
        return " ".join([word for word in cleansentence if '@' not in word and 'http' not in word and  'RT' not in word and '#' not in word])
    
