import requests, bs4, wikipedia, re, random

UK_wars = 'https://en.wikipedia.org/wiki/List_of_wars_involving_the_United_Kingdom'

##def wars_from_tbody(tbody):
##    war_links = []
##    tr = tbody.findAll('tr')
##    #could risk first link in every row.
##    for war in tr:
##        war_links.append(war.find('a'))
##    print(len(war_links),'wars found.')
##    return war_links

def get_wars_from_list(war_list):
    links = []
    source = requests.get(war_list)
    source.raise_for_status()
    soup = bs4.BeautifulSoup(source.text,'lxml')
    tables = soup.findAll('table')
    #print(len(tables))
    
    for table in tables[:-1]: #last table promotes links.
        print(type(table))
        #print(table)
        #table_soup = bs4.BeautifulSoup(table.text,'lxml')
        trs = table.findAll('tr')
        print(type(trs))
        for tr in trs:
            row = tr.find("td")
            if isinstance(row, bs4.element.Tag) or isinstance(row, bs4.element.ResultSet):
                link_list = row.findAll("a")
                war_list = [link['href'] for link in link_list]
                #war_list = [link.contents[0] for link in link_list]
                links.extend(war_list)
    scrubbed_links = [l for l in links if l[0]=='/']
    #scrubbed_links = [l for l in links if l[0]!='[']#NOT VERY GENERAL ONLY ELIMINATE CITATIONS.
    return(scrubbed_links)
        
        #print(type(tb))
        #table_soup = bs4.BeautifulSoup(tb.text,'lxml')
        #trs = table_soup.findAll('tr')
##        for tr in trs:
##            links.append(tr.find('a'))
        

##    for i in tbods:
##        print(type(i))
##        tr = i.findAll('tr')
##        for war in tr:
##            war_links.append(war.find('a'))
##        print(len(war_links),'wars found.')

    print(len(links), 'in total.')
        

def get_soup(pg):
    '''string input, will pick first suggested page and look for belligerents in infobox.
    Returns VERY unclean list of belligerents. Non-discriminatory.
    '''   
    search = wikipedia.search(pg)[0]
    print(search)
    page = wikipedia.page(search)
    page_soup = bs4.BeautifulSoup(page.html(), 'lxml')

    info_box = page_soup.find('table',class_='infobox vevent')

    rows = info_box.findAll('tr')

    ##for row in rows:
    ##    data = row.find_all('td')
    ##    r = [i.text for i in data]
    ##    print(r)

    info_headers = info_box.findAll('th')

    for info_head in info_headers:
        if info_head.text == 'Belligerents': #No Garuntee
            belligerent = info_head.find_parent('tr')
            belligerent_row = belligerent.find_next_sibling('tr')
            bel_lists = belligerent_row.findAll('td')
            return bel_lists

    #if code gets to here, no belligerents, not a scrapably war page.

def get_soup_from_href(pg):
    '''string input, will pick first suggested page and look for belligerents in infobox.
    Returns VERY unclean list of belligerents. Non-discriminatory.
    '''
    l = 'https://en.wikipedia.org' + pg
    source = requests.get(l)
    source.raise_for_status()
    
##    search = wikipedia.search(pg)[0]
##    print(search)
##    page = wikipedia.page(search)
    page_soup = bs4.BeautifulSoup(source.text, 'lxml')

    info_box = page_soup.find('table',class_='infobox vevent')

    rows = info_box.findAll('tr')

    ##for row in rows:
    ##    data = row.find_all('td')
    ##    r = [i.text for i in data]
    ##    print(r)

    info_headers = info_box.findAll('th')

    for info_head in info_headers:
        if info_head.text == 'Belligerents': #No Garuntee
            belligerent = info_head.find_parent('tr')
            belligerent_row = belligerent.find_next_sibling('tr')
            bel_lists = belligerent_row.findAll('td')
            return bel_lists

    #if code gets to here, no belligerents, not a scrapably war page.
        
def hasNumbers(string): #It seems no nations have numbers in their names, this is typically indicative of citations or dates.
    return bool(re.search(r'\d', string))

def faction_split(faction):
    '''receive either the victor or vanquished fanction and return a workable list.'''
    faction_list = []
    for nation in faction:
        if nation.parent.name == 'b' or nation.parent.name == 'small':
            continue
        if len(nation.text)>4 and not hasNumbers(nation.text) and nation.text!='citation needed':
            faction_list.append(nation.text)

    return faction_list



##test_cases = ['world war one','hundred days','pontiac\'s rebellion','Ottoman-Persian War','Taiping_Rebellion','Pahang Civil War']
##
##pg = random.choice(test_cases)
##victor,vanquished = get_soup(pg)
##vi_nations = victor.findAll('a')
##va_nations = vanquished.findAll('a')
##
##victor_list = faction_split(vi_nations)
##vanquished_list = faction_split(va_nations)
##
##print(victor_list)
##print('-'*20)
##print(vanquished_list)

wars_UK = get_wars_from_list(UK_wars)
synonyms = ['British','Great Britain','United Kingdom','British Empire','Royal Navy','British East India Company']

win_lose = {}
win_lose['won'] = 0
win_lose['lost'] = 0

for war in wars_UK:

    try:
        victor,vanquished = get_soup_from_href(war)
        vi_nations = victor.findAll('a')
        va_nations = vanquished.findAll('a')

        victor_list = faction_split(vi_nations)
        vanquished_list = faction_split(va_nations)

        if(len([b for b in synonyms if b in victor_list])>0):
            win_lose['won'] += 1
        if(len([b for b in synonyms if b in vanquished_list])>0):
            win_lose['lost'] += 1

##        if len([b in synonyms for b in victor_list])>0:
##            win_lose['won'] += 1
##        if len([b in synonyms for b in vanquished_list])>0:
##            win_lose['lost'] += 1
        
        print(win_lose)
        print('...',war,'\n')
        print(victor_list)
        print('-'*20)
        print(vanquished_list)
        
    except ValueError:
        print('War does not have 2 sides.')
    except AttributeError:
        print('No infobox to scrape for this skirmish.')
    except wikipedia.DisambiguationError:
        print('War search to ambiguous, use href.')
    except TypeError:
        print('Unscrapable Box')
    except:
        print('Unexpected Error')
        

    print('\n'*2)



        
