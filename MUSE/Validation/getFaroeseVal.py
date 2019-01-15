import urllib2
from bs4 import BeautifulSoup
import json
import re



def findWord(exp):
    exp =  re.sub(r'[<span .*/span> |<i>.*</i> ]', "", exp)
    word =  exp.split(",")[0].encode("utf8")
    return word


def findTranslation(word):
    url = "https://sprotin.fo/dictionary_search_json.php?DictionaryId=3&DictionaryPage=1&SearchFor="+ word + "&SearchInflections=0&SearchDescriptions=0&Group=&SkipOtherDictionariesResults=1&SkipSimilarWords=0"

    response = urllib2.urlopen(url)

    # soup = BeautifulSoup(page, 'html.parser')
    #
    #
    # name_box =  soup.find("div", {"class": "dictionary-results--word-description"})
    data = json.loads(response.read())

    if data["status"] == "success":

        exp = data["words"][0]["Explanation"]
        return exp.rstrip()
    else:
        return None
        # print word + " not found"

with open("fa-en.txt", "w") as w:
    with open("de-en.5000-6500.txt", "r") as r:
        line = r.readline()
        count = 0
        while line:

            en_word = line.split(" ")[1].strip("\n")
            fa_word = findTranslation(en_word)




            if fa_word:
                if "\n" in fa_word:
                    word = ""
                    for i in fa_word.split("\n"):
                        word += i
                    fa_word = word

                w.write("[" + en_word + "~" + fa_word.encode("utf8") +  "]\n")

            line = r.readline()
            count += 1
            print count
