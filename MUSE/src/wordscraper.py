# import libraries
import urllib2
from bs4 import BeautifulSoup
import re

gratis_Counter = 0
betaald_Counter = 0
cleanr = re.compile('<.*?>')

# https://dimma.fo/
# Betaalde artikelen = 1672
# Gratis artikelen = 5202

# quote_page = 'https://dimma.fo/heimatidindi/'
# Betaalde artikelen = 901
# Gratis artikelen = 3224

# https://dimma.fo/uttanlands/
# Betaalde artikelen = 199
# Gratis artikelen = 728

# https://dimma.fo/kjak/
# Betaalde artikelen = 188
# Gratis artikelen = 536

# https://dimma.fo/mentan/
# Betaalde artikelen = 240
# Gratis artikelen = 664

# https://dimma.fo/langlesnadur/
# Betaalde artikelen = 325
# Gratis artikelen = 0

# https://dagur.fo/innanlands
# 1875

# https://dagur.fo/uttanlands/
# 598

# https://dagur.fo/

# fiskur.fo




with open('linksWrite.txt', 'r') as r:
    with open('roysni_annad.txt', 'w') as w:
        url  = r.readline()
        while url:
            if "roysni" in url:
                print url
                print '\n\n'
                try:
                    page = urllib2.urlopen(url)


                    soup = BeautifulSoup(page, 'html.parser')

                    # Take out the <div> of name and get its value
                    free_content = soup.find('div', attrs={'class':'content-wrap'})

                    login_content = soup.find('section', attrs={'class':'not-logged-preview'})

                    if free_content is not None:
                        print "Gratis scanned" + str(gratis_Counter)
                        gratis_Counter += 1

                        free_content  =  re.sub(cleanr, '', str(free_content))
                        w.write(str(free_content))
                        w.write("\n")
                    else:
                        additional_content = soup.find('div', attrs={'class':'additional-content'})
                        print "Betaald scanned" + str(betaald_Counter)
                        betaald_Counter += 1

                        login_content  =  re.sub(cleanr, '', str(login_content))
                        additional_content  =  re.sub(cleanr, '', str(additional_content))

                        w.write(str(login_content))
                        w.write("\n")
                        w.write(str(additional_content))
                        w.write("\n")

                except Exception as e:
                    pass

                # for i in name_box:
                #     # link = i.find('a')
                #     # if link:
                # # if '//dimma' in str(link):
                #     # w.write(str(i))
                #     # w.write('\n')
                #     print i

            url = r.readline()



# name = name_box.text.strip() # strip() is used to remove starting and trailing
#
# with open('linksWrite.txt', 'w') as w:
#     for i in name_box:
#         print str(i)
#         w.write(str(i))
#         w.write('\n')
# # https://medium.freecodecamp.org/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe
