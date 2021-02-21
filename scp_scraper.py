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
#from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

driver = webdriver.Chrome(r"C:\Users\Julio Hong\chromedriver_win32\chromedriver")
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
thousands_digit = 0

for link in series_links:
    # Indicates scraping loop start
    print('Start ' + link.split('net')[-1] + ' at ' + str(dt.datetime.now()))
    # Open the webpage of the SCP Series #
    driver.get(link)
    
#    # This basically looks for the text of the link, which may not necessarily follow the SCP-#### format.
#    # So some number entries are missing.
#    series_names = driver.find_elements_by_xpath("//*[contains(text(), 'SCP-')]")
    
    # What I actually want is simple: Copy the link text, and then copy the text after that.
    # Find all the li's, which are elements that contains the text 'SCP-'
    series_names = driver.find_elements_by_xpath("//*[contains(text(), 'SCP-')]")
    # Moves one level down to a href and text
    series_names = [x.find_element_by_xpath("..") for x in series_names]
    print(len(series_names))
    series_names = series_names[:-1]
    print(len(series_names))
    series_text = series_names.copy()
    # Copies the text attribute of the li (which includes the text holding the embedded link)
    series_text = [x.text for x in series_names]
    # Need to remove SCP-EX which is always the final entry

#    print(series_text)
    
    # The number usually comes before the dash
    series_nums = [x.text.split(' - ')[0] for x in series_names]
    # The name usually comes after the dash
    series_names = [x.text.split(' - ')[-1] for x in series_names]
    print(series_nums)
        
#    while 'SCP-EX' in series_nums:
#        series_nums.remove('SCP-EX')
    
    # Check the sum of series_num using the formula: (x1+xn)*(n/2)
    # Replace thousands digit with the final number, except for the first series where the final char is the letter 's'
    # Then thousands_digit = 0 based on initialisation
    if link[-1] != 's':
        thousands_digit = int(link[-1])
    print(link[-1])

#    series_sum_check = (0 + 999 + 2*1000*thousands_digit) * (1000/2)
    series_sum_check = plusone_series_sum(0 + thousands_digit*1000, 999 + thousands_digit*1000)
    series_nums_only = [int(x.split('-')[-1]) for x in series_nums]
    if series_sum_check - sum(series_nums_only) != 0:
        print(str(series_sum_check) + ' vs ' + str(sum(series_nums_only)))
        print('Missing SCP entry!')
        
#    series_nums_only = [int(x.split('-')[-1][4]) if len(x.split('-')[-1]) > 3 else int(x.split('-')[-1]) for x in series_nums]
#    if link[-1] != 's':
#        series_nums_only = [x.split('-')[-1][:4] for x in series_nums]
#    else:
#        series_nums_only = [x.split('-')[-1] for x in series_nums]
#    print('Sum-check series numbers: ' + str(sum(series_nums_only)) + ' vs. ' + str(series_sum_check))
    
    scip_nums = scip_nums + series_nums   
    scip_names = scip_names + series_names
    
    many_series.append(series_text)
    
    print('End at ' + str(dt.datetime.now()))


scip_nums_only = [int(x.split('-')[-1]) for x in scip_nums]
# List sum-checker using binary search
# I think recursion is better in this case
def list_sum_check(int_list):
#    while first_half_sum_check != 0 or second_half_sum_check != 0:
    # Split the list in two
    first = 0
    last = len(int_list)
    mid = (first + last - 1) // 2 + 1
    print({'First':first, 'Mid':mid-1, 'Last':last-1})
    
#    print(sum(int_list[mid:last]))
#    print(arith_series_sum(int_list[mid+1], int_list[last]))
#    print(sum(int_list[mid:last]) - arith_series_sum(int_list[mid+1], int_list[last]))
    
    # Compares the sum of the list against the theoretical sum based on first and last elements
    first_half_sum_check = sum(int_list[:mid]) - plusone_series_sum(int_list[first], int_list[mid-1])
    second_half_sum_check = sum(int_list[mid:last]) - plusone_series_sum(int_list[mid], int_list[last-1])
    
    # Split list in two and sum-check each one
    if first_half_sum_check != 0:
        print("First half: " + str(first_half_sum_check))
    if second_half_sum_check != 0:
        print("Second half: " + str(second_half_sum_check))

# Too many things could go wrong. Instead, I need to work from the data set I have.
# Also, if there's no SCP-# given, just take it from the link. (Find index in names and then corresponding element in nums)
def scpseries_sum_check(int_list):
    # To think about things recursively, start from the simplest case
    # A list of 1 element or 2 elements will always return zero delta
    # A list of 3 elements might not though. But how will it be split?
    # It won't be split. It'll just take the sum and whatnot
    # Mid is just to split this in half.
    # Split the list in two
    first = 0
    last = len(int_list) - 1
    mid = (first + last) // 2
    print({'First':first, 'Mid':mid, 'Last':last})
    
    # Create a theoretical list.
    # Need to come up with the possibilities: What if the error is first, or last? Or 2nd in a list of 3?
    # Check if error is first or last by doing a check: last-first+1 == len(list)?
    # If true, then the error is in the middle.
    # Else, determine if it's first or last.
    # What about multiple errors?

    # Compares the sum of the list against the theoretical sum based on first and last elements
    if len(int_list) == 3:
        series_sum_check = sum(int_list[:last+1]) - plusone_series_sum(int_list[first], int_list[last])
        theoretical_mid = int_list[first] + mid
        if series_sum_check != 0:
            print('Mid element is '+ str(int_list[mid]) + ' instead of ' + str(theoretical_mid))
    
    # Need to split the list in two. But how to avoid splitting into lists of 2 elements?
    # Maybe have a special case that will include
#    else:

        
        
        

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