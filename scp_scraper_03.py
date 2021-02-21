# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 09:42:05 2019

@author: Julio Hong
"""

# SCP Web Scraper
# Purpose:
# Learning Outcome: Become more familiar with web scraping. Also create an overview of the SCPs currently in the database.
# For some reason the pip installed to my AppData folder instead of the Anaconda folder, and I couldn't import these libs.
# Only after transfer then I could import.
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

driver = webdriver.Chrome(r"C:\Users\Julio Hong\chromedriver_win32\chromedriver.exe")
scp_series01 = 'http://www.scp-wiki.net/scp-series'

# Get all SCP Names
# ==============================
# Find all the SCP Series pages available

# Might need a companion doc to help break down the webpage.
# (Low prio if not expected to change)
# Go to the webpage of SCP Series I
driver.get(scp_series01)
# Locate the sidebar which covers the boxes on the left side: Main, User Resouces, Social Media and Languages
side_bar = driver.find_element_by_id("side-bar")
# Locate the first box which is Main
side_block = side_bar.find_elements_by_class_name("side-block")[0]
# Brutal way to reach this, and haven't even extracted the links.
# Find the text of the heading called 'SCP by Series'
scp_series_body = side_block.find_element_by_xpath("//p[contains(text(), 'SCP by Series')]")
# Go up one hierarchy level to the heading object itself
scp_series_body = scp_series_body.find_element_by_xpath("..")
# Move to the next menu-item which contains all the SCP Series links
# FYI as of Feb'20, SCP Series VI is online following the conlcusion of the SCP-5000 contest: Mystery
scp_series_body = scp_series_body.find_element_by_xpath("following-sibling::*")
# Move down one level again and find all the objects within.
# Length of this list should correspond to the number of links + the papers icon at leftmost
scp_series = scp_series_body.find_elements_by_xpath(".//*")
# Starting from the 2nd element, get the text within the href attribute which is a link
#for x in scp_series[1:]:
#    print(x.get_attribute('href'))
series_links = [x.get_attribute('href') for x in scp_series][1:]
# Find the total number of scips based on number of SCP Series
num_of_scips = len(series_links) * 1000 - 1
# Added a new column called Link_Name which is usually equal to the SCP number, but might be different
scips = pd.DataFrame(index=[str(x).zfill(3) for x in range(num_of_scips)],columns=['Number','Link_Name','Name','Object_Class','Length','Tags','Outgoing_Links','Other_SCPs'])
#scips.loc['000','Name'] = 'SCP-000'


# Initialise the SCP dataframe, which will store number, name, classification, maybe length of article, outgoing links, links to other SCPs and tags.
# Attempt #1
#for link in series_links:
#for link in ['http://www.scp-wiki.net/scp-series']:
#    for scip_num in scips.index[1:]:
#        scip_linkname = 'SCP-' + scip_num
#        scip_name = driver.find_element_by_xpath("//*[contains(text(), '%s')]" % scip_linkname)
#        scip_name = scip_name.find_element_by_xpath("..")
#        scip_name = scip_name.text.split(' - ')[-1]
#        scips.loc[scip_num,'Name'] = scip_name

# Attempt #2
#names = ['SCP-000']
#print(dt.datetime.now())
#for link in ['http://www.scp-wiki.net/scp-series']:
#    for scip_num in scips.index[1:]:
#        scip_linkname = 'SCP-' + scip_num
#        scip_name = driver.find_element_by_xpath("//*[contains(text(), '%s')]" % scip_linkname)
#        scip_name = scip_name.find_element_by_xpath("..")
#        scip_name = scip_name.text.split(' - ')[-1]
#        names.append(scip_name)
#        print(dt.datetime.now())


# Arithmetic series summer
def plusone_series_sum(start, end):
    sum_of_series = 0
    for num in range(start, end+1):
        sum_of_series += num
    return sum_of_series


# Attempt #3
# Handle SCP-000 which isn't listed
scip_names = ['SCP-000']
scip_nums = ['SCP-000']
#many_series = []
thous_dgt = 2

for link in series_links[thous_dgt:]:
#for link in series_links:
    # Indicates scraping loop start
    print('Start ' + link.split('net')[-1] + ' at ' + str(dt.datetime.now()))
    # Open the webpage of the SCP Series #
    driver.get(link)
    
    # Copy the SCP name
    # Find all the li's, which are elements that contains the text 'SCP-'
    series_names_raw = driver.find_elements_by_xpath("//*[contains(text(), 'SCP-')]")
    # Moves one level down to a href and text
    series_names = [x.find_element_by_xpath("..") for x in series_names_raw]
    # Need to remove SCP-EX which is always the final entry
    print('Check number of entries before and after removing SCP-EX')
    print(len(series_names))
    series_names = series_names[:-1]
    print(len(series_names))

    series_text = series_names.copy()
    # Copies the text attribute of the li (which includes the text holding the embedded link)
    series_text = [x.text for x in series_names]
#    print(series_names[0].get_attribute('href'))
#    series_links = [x. for x in series_names]

# Get all attributes with BS4
#    html = series_names[0].get_attribute('outerHTML')
#    attrs = BeautifulSoup(html, 'html.parser').a.attrs
#    print(html)
#    print(attrs)
#    print(attrs['href'][5:])
#    print(series_names[0].get_attribute(''))
    
    # Take number directly from link (maybe get link attribute)
    series_nums_raw = [BeautifulSoup(x.get_attribute('outerHTML'), features='lxml') for x in series_names]
    
    if thous_dgt == 2:
        print(series_nums_raw[225:250])
        print(series_nums_raw[550:575])
        print(series_nums_raw[700:725])
    
    series_nums = [BeautifulSoup(x.get_attribute('outerHTML'), features='lxml').a.attrs['href'][1:] for x in series_names]
    
#    series_nums = [int(x.split('-')[0]) for x in series_nums]
    # Use nested list comprehension
#    print(series_nums[225:250])
    series_nums = [x.split('-') for x in series_nums]
#    print(series_nums[225:250])
    series_nums = [int(y) for little_list in series_nums for y in little_list if y.isdigit()]
#    series_nums = [int(x) for x in series_nums if x.isdigit()]
    
    print(series_nums)
#     The links aren't all playing ball with me.
#    series_nums = [int(x) for x in series_nums]
    # Check the series_nums using a theoretical table
#    print(link)
    if link[-1] != 's':
        theory_series_nums = [x for x in range(thous_dgt*1000, (thous_dgt+1)*1000)]
    # Series I link ends with 's': http://www.scp-wiki.net/scp-series
    # Series I starts at SCP-001
    else:
        theory_series_nums = [x for x in range(1,1000)]
    # Extend delta list to length of actual list to properly subtract elemnents
    extra_nums = len(series_nums) - 1000
    for x in range(extra_nums):
        theory_series_nums.append(0)
#    delta_series_nums = [actual - theory for actual, theory in zip(series_nums, theory_series_nums)]
#    print(delta_series_nums)
    
    # Find extra numbers in the series_nums
    delta_series_nums = [1]
    prev_delta_sum = 999999
    # Use count to cap the number of repeats
    count = 0
    while sum(delta_series_nums) != 0 and count < 5:
#    while sum(delta_series_nums) != 0:
        # Compare list against theoretical list to get delta list
        delta_series_nums = [actual - theory for actual, theory in zip(series_nums, theory_series_nums)]
        print(delta_series_nums)
        # For delta list with nonzero sum/max, find the last zero element and its index 
#        if sum(delta_series_nums) != 0:
#            last_zero_delta = next(i for i in reversed(range(len(delta_series_nums))) if delta_series_nums[i] == 0)
        if sum(delta_series_nums) == 0:
            break
        last_zero_delta = next(i for i in reversed(range(len(delta_series_nums))) if delta_series_nums[i] == 0)
        # Insert a zero at that index+1 in the theoretical list 
        theory_series_nums.insert(last_zero_delta+1, 0)
        # Compare against previous sum: If same, break
        if sum(delta_series_nums) == prev_delta_sum:
            break
        prev_delta_sum = sum(delta_series_nums)
        
        count += 1
    
    # Remove extra numbers from series_nums
    outliers = [x for x in delta_series_nums if x != 0]
    print(outliers)
    for guy in outliers:        
        print(delta_series_nums.index(guy))
        series_nums.remove(delta_series_nums.index(guy)+1)
    print(series_nums)
        
    scip_nums = scip_nums + series_nums   
    scip_names = scip_names + series_names
    thous_dgt += 1
        
    print('End at ' + str(dt.datetime.now()))
























# Actually tags will be really useful for organising.
# Other parameters may include certain keywords or names of renowned Agents, Overseers or mentions to the Administrator.
# Links to supplements or SCPs will be stored in their own respective dictionaries, so just indicate with Y/N, then use SCP-# as dict key.
# I might put a placeholder at SCP-000, which actually does have a page but isn't listed.
# Loop through each series
# Find the string 'SCP-#', then store the number and name in a df

# Export to CSV. Can rebuild from CSV later on.

# Can construct link using only the number.



# Links to supplements/other SCPs/tags
# ==============================
# Key: SCP-#; Value: List containing all the other links.
# I have to do this because cannot store lists as a df entry.
# Create a suplm_dict
# Create another_SCP_dict
# Create a tags_list. This one is actually important for further categorisation.

# I'll have to skip SCP-001 for now. It's like a mini-database on its own.