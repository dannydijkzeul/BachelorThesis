import glob
import os
import re

path = "Faroese-Language-Corpus"

with open("faroesOneFile+scraped.txt", "w") as w:
    i = 0
    for filename in glob.glob(os.path.join(path, '*.txt')):
      print(filename)
      with open(filename, "r") as f:
          line = f.readline()

          while line:
              # reLine = re.sub(r',|<|>|\.|"|[0-9]|-|\?|!|\s\n|\'|<\s>|“|„|(|)','',line)
              i += 1
              print(filename + "    " +  str(i))
              w.write(line)
              line = f.readline()

    i = 0
    for filename in glob.glob(os.path.join("Portal Scraped", '*.txt')):
      print(filename)
      with open(filename, "r") as f:
          line = f.readline()

          while line:
              # reLine = re.sub(r',|<|>|\.|"|[0-9]|-|\?|!|\s\n|\'|<\s>|“|„|(|)','',line)
              i += 1
              print(filename + "    " +  str(i))
              w.write(line)
              line = f.readline()




#  Sentences fareur  636305
#  Words fareur in Fasttext 71654
#  Senteces English
# Words in English in Fasttext 421377


#  Urdu sentences paper 5.5 million, Romainian is 2.2 million
