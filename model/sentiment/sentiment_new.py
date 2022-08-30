#%%
import os, pandas as pd, numpy as np, itertools, sys
from operator import itemgetter
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class Sentiment:
#%%
       def __init__(self):
              self.factory = StemmerFactory()
              self.stemmer = self.factory.create_stemmer()
              self.THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
              self.df_polarity = pd.read_excel(os.path.join(self.THIS_FOLDER,'sangkalan_and_degree_of_affection.xlsx'), "sangkalan")
              self.df_degree = pd.read_excel(os.path.join(self.THIS_FOLDER,'sangkalan_and_degree_of_affection.xlsx'), "degree_of_affection")
              self.df_affective = pd.read_excel(os.path.join(self.THIS_FOLDER,'adjective.xlsx'),'affective_space2')
              self.df_russel = pd.read_excel(os.path.join(self.THIS_FOLDER,'adjective.xlsx'),'Russel')
              self.df_stopwords = pd.read_excel(os.path.join(self.THIS_FOLDER,'stopwords.xlsx'))
              self.df_stopwords = self.df_stopwords['kata'].values.tolist()
              self.df_query_tweet = pd.DataFrame(columns=[list(self.df_affective.columns)])

       #%%
       def deleteSymbol(self, sentence):
              #Menghapus simbol
              symbol = ['”', '$', '%', '&', '’', '(', ')', '*', '+','/', ':', ';', '<', '=', '>', '@', '[', "RT ", ']', '^', '_', '`', '{', '|', '}', '~']
              for i in symbol : 
                     sentence = sentence.replace(i, '')   
              return sentence

       #%%
       def numberConverter(self, sentence):
              #Menghapus angka
              number = ['1','2','3','4','5','6','7','8','9','0']
              for i in number : 
                     sentence = sentence.replace(i, '')   
              return sentence

       #%%
       def removeAffixNya(self, sentence): #bkn rule
       # Remove affixes nya except for word harus
              excep= ['harus', 'ha', 'ta']
              return ' '.join([word.replace("nya",'') for word in sentence.split(" ") if word not in excep])

       #%%
       def removeMentions(self, sentence): #bkn rule
       # Remove account mentions in sentence
              return (' '.join([word for word in sentence.split(" ") if '@' not in word and 'http' not in word and '#' not in word ]))

       #%%
       def preprocessing(self, sentence):
              sentence = self.removeMentions(str(sentence).lower())
              sentence = self.deleteSymbol(sentence)
              sentence = self.numberConverter(sentence)
              return sentence

       #%%
       def dotAndCommaBreak(self, sentence):
              # Dot and Comma Break Rule
              sentence = str(sentence).replace('.',',').replace('!',',').replace('?',',').replace("  ",' ')
              sentencebreak = [word.strip() for word in sentence.split(',')]
              return list(filter(None, sentencebreak))
       #%%
       def filtering(self, words):
              for word in words:
                     if word in self.df_stopwords:
                            words.remove(word)
              return words
       #%%    
       def stemmingWord(self, word):
              word = self.stemmer.stem(' '.join(word))
              return word.split(" ")

       def terimakasihPosition(self, sentence):
              # Check word terimakasih position in sentence
              try:
                     try:
                            if sentence.split(" ").index("terimakasih") == 0:
                                   return 1
                     except ValueError:
                            idxterima = sentence.split(" ").index("terima")
                            idxkasih = sentence.split(" ").index("kasih")
                            if idxterima+1 == idxkasih and idxterima == 0:
                                   return 1
              except:
                     return 0
       #%%
       def getPolarityDegree(self, word_value, words, idx):
              index_sebelum = idx-3
              if(index_sebelum<0):
                     index_sebelum = 0
              for word in words[index_sebelum:idx+2]:
                     # print(word)
                     if not self.df_degree[(self.df_degree['kata'] == word)].empty:
                            if(word_value < 0):
                                   word_value = (abs(word_value) + self.df_degree.loc[self.df_degree['kata'] == word,'nilai'].iloc[0])*-1
                            else:
                                   word_value = word_value + self.df_degree.loc[self.df_degree['kata'] == word,'nilai'].iloc[0]
                            # print(word_value,"TRUE Degree")
              if(idx+1 == len(words) - 1 ):
                     idx = idx+3
              for word in words[index_sebelum:idx]:
                     if not self.df_polarity[(self.df_polarity['kata'] == word)].empty:
                            word_value = self.df_polarity.loc[self.df_polarity['kata'] == word,'nilai'].iloc[0]*word_value
                            # print(word_value,"TRUE polarity")
              # print(word_value)
              return word_value   
       #%%
       def affectiveValue(self, words, istc):
              word_value = 0
              for idx,word in enumerate(words):
                     df = self.df_affective[(self.df_affective['value'] == word)]
                     if not df.empty:
                            wordval = df.sum(axis = 1, skipna = True).iloc[0]
                            word_value += self.getPolarityDegree(wordval,words,idx)
                            # print("Kata sifat: ", word, "Value: ", word_value)
              return word_value

       #%%
       def getSentiment(self, sentence):
              totalsentiment = 0
              sentence_pre = self.preprocessing(sentence)
              sentencebreak = self.dotAndCommaBreak(sentence_pre)
              sentimentval = 0
              for istc, sentenceb in enumerate(sentencebreak):
                     skipIndex = []
                     # print("============================================================")
                     # print("Klausa: ", sentenceb)
                     if (self.terimakasihPosition(sentenceb) == 1 and istc == 0):
                            sentenceb.replace("terima", "")
                            sentenceb.replace("kasih", "")
                            sentimentval += 1
                     word = list(filter(None, sentenceb.split(" ")))
                     word = [item for item in word]
                     word = self.filtering(word)
                     word = self.stemmingWord(word)
                     value = self.affectiveValue(word, istc)
                     sentimentval+=value
                     # print("Value: ", sentimentval)
                     #sanitising
              totalsentiment+=sentimentval
              return(totalsentiment)

#%%
# df_tweet = pd.read_excel('tweet_clean.xlsx','test')
# tweet_old = pd.read_csv('tweetbpjs.csv')
# tweet_new = pd.read_csv('tweet_new.csv')
# df_tweet = tweet_old.append(tweet_new, ignore_index = True) 
# df_sentiment = pd.DataFrame(columns=('sentence', 'created_at', 'sentiment'))
# for index in df_tweet.index:
#     print("----------------------------------------------------------------")
#     print(df_tweet.loc[index,'full_text'])
#     sentence, sentiment = getSentiment(df_tweet.loc[index,'full_text'])
#     df_sentiment = df_sentiment.append({'sentence': sentence, 'sentiment': sentiment, 'created_at': df_tweet.loc[index,'created_at']}, ignore_index=True)
# df_sentiment.to_excel("output_sentiment_xy_new.xlsx", index=False)
#getSentiment("@KenDedez @humaira979 @HerryPradono @anak__perantau @jokowi @KemenkeuRI @BPJSKesehatanRI Betul, sistem itu perlu ditingkatkan makanya BPJS selalu membuka diri utk dikritik dan diberi masukan. Sebelum ada BPJS, masyarakat malas ke RS karena biaya besar. Skrg dijamin oleh negara makanya banyak yg berobat. Utk menipu itu tergantung pribadi dan hati nurani kita.. Ok")

# %%
