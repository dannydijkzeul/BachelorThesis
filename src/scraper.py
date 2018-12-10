# import libraries
import urllib2
from bs4 import BeautifulSoup
import re

cleanr = re.compile('<img .*>|<a href="|">|<.*?>')

quote_page = 'https://roysni.fo/annad/'

with open('linksWrite.txt', 'w') as w:

    for numberPage in range(1,35):

        page = urllib2.urlopen(quote_page + str(numberPage))

        soup = BeautifulSoup(page, 'html.parser')

        # Take out the <div> of name and get its value
        name_box = soup.findAll( 'article')
        # print name_box

        print quote_page + str(numberPage)
        print "\n\n"

        for i in name_box:
            link = i.find('a')
            if link:
                if '//roysni' in str(link):
                    link  =  re.sub(cleanr, '', str(link))
                    w.write(str(link))
                    w.write('\n')



# name = name_box.text.strip() # strip() is used to remove starting and trailing
#
# with open('linksWrite.txt', 'w') as w:
#     for i in name_box:
#         print str(i)
#         w.write(str(i))
#         w.write('\n')
# # https://medium.freecodecamp.org/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe
