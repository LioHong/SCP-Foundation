# -*- coding: utf-8 -*-
"""
Filename: scp_scraper_05.py
Created on Tue Aug 4 01:51:36 2020
@author: Julio Hong
Purpose: Become more familiar with web scraping. Also create an overview of the SCPs currently in the database.
Steps: 
For some reason the pip installed to my AppData folder instead of the Anaconda folder, and I couldn't import these libs.
Only after transfer then I could import.
"""

from selenium import webdriver
import pandas as pd
import datetime as dt
import re
import scp_page_scraper as sps
from logging import getLogger

# To adjust the dataframe appearance
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 200)

driver = webdriver.Chrome(r"C:\Users\Julio Hong\chromedriver_win32\chromedriver.exe")
scp_series01 = 'http://www.scp-wiki.net/scp-series'

# Get all SCP Names
# ==============================
# Find all the SCP Series pages available
# Read companion doc scp_scraper_DOC.odt to help break down the webpage.
# (Low prio if not expected to change)
# Go to the webpage of SCP Series I
driver.get(scp_series01)
# Locate the sidebar which covers the boxes on the left side: Main, User Resources, Social Media and Languages
side_bar = driver.find_element_by_id("side-bar")
# Locate the first box which is Main
side_block = side_bar.find_elements_by_class_name("side-block")[0]
# Brutal way to reach this, and haven't even extracted the links.
# Find the text of the heading called 'SCP by Series'
scp_series_body = side_block.find_element_by_xpath("//p[contains(text(), 'SCP by Series')]")
# Go up one hierarchy level to the heading object itself
scp_series_body = scp_series_body.find_element_by_xpath("..")
# Move to the next menu-item which contains all the SCP Series links
# FYI as of Feb'20, SCP Series VI is online following the conclusion of the SCP-5000 contest: Mystery
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
# scips = pd.DataFrame(index=[str(x).zfill(3) for x in range(num_of_scips)],columns=['Number','Link_Name','Name','Object_Class','Length','Tags','Outgoing_Links','Other_SCPs'])

#scips.loc['000','Name'] = 'SCP-000'


# Initialise the SCP dataframe, which will store number, name, classification, maybe length of article, outgoing links, links to other SCPs and tags.

# =============================================================================
# Attempt #5

# Generates an arithmetic sequence with missing entries/dupes as desired
def gen_seq_with_missing(arith_seq_list, missing_entries=[], removal_switch='value'):
    # Count updates the index entries as the list grows shorter
    count = 0
    for entry in missing_entries:
        if removal_switch == 'value':
            arith_seq_list.remove(entry)
        elif removal_switch == 'index':
            arith_seq_list.pop(entry - count)
            count += 1
        else:
            print('Invalid input for removal_switch.')
    return arith_seq_list

def gen_seq_with_dupes(arith_seq_list, dupes_dict, dupe_switch: str):
    for index in dupes_dict:
        if dupe_switch == 'replace':
            arith_seq_list.pop(index)
            arith_seq_list.insert(index, dupes_dict[index])
        elif dupe_switch == 'insert':
            arith_seq_list.insert(index, dupes_dict[index])
    return arith_seq_list

# missing_entries maybe change to dict, or represent duped entries as a dict within the list
def gen_arith_seq(start_num, end_num, action: str, outliers={}):
    # Creates a list of sequential integers
    arith_seq_list =[x for x in range(start_num, end_num+1)]

    # If there are no missing entries, return the list.
    if len(outliers) == 0:
        return arith_seq_list
    
    # Removes the integers based on the outliers  
    # Check if removal is based on the index or value    
    elif action.split('_')[0].lower() == 'remove':
        arith_seq_list = gen_seq_with_missing(arith_seq_list, outliers, action.split('_')[-1])
        
    elif action.split('_')[0].lower() == 'dupe':
        arith_seq_list = gen_seq_with_dupes(arith_seq_list, outliers, action.split('_')[-1])
    
    # Might want to generate sequences with both missing entries and dupes (assume in that order)
    elif action.split('_')[0].lower() == 'stack':
        # Remove entries first
        missing_entries = outliers['remove']
        if 'value' in action:
            arith_seq_list = gen_seq_with_missing(arith_seq_list, missing_entries, removal_switch='value')
        elif 'index' in action:
            arith_seq_list = gen_seq_with_missing(arith_seq_list, missing_entries, removal_switch='index')
        
        # Then add dupes
        dupes_dict = outliers['dupe']
        if 'replace' in action:
            arith_seq_list = gen_seq_with_dupes(arith_seq_list, dupes_dict, dupe_switch='replace')
        elif 'insert' in action:
            arith_seq_list = gen_seq_with_dupes(arith_seq_list, dupes_dict, dupe_switch='insert')
    
    return arith_seq_list

def find_outliers(template_nums, series_nums):
    # This has to deal with lists that are too short/long, and find out if entries are missing/duped
    # Compare the list lengths
    theory_nums = template_nums.copy()
    actual_nums = series_nums.copy()

    # New approach. We use set() to find dupes, of which there are two kinds
    # 1) Dupe within the series and 2) Dupe outside of the series
    # The second type is actually easier to find
    # Just check the thousands digit
    thous_check = [x // 1000 for x in actual_nums]
    non_series_val = [x for x in thous_check if x != theory_nums[0] // 1000]
    nsv_dict = {}
    for nsv in non_series_val:
        nsv_idx = thous_check.index(nsv)
        nsv_dict[nsv_idx] = nsv
        # Remove the nsv to check for identical values later on
        thous_check[nsv_idx] = 1
    # Replace the values with the dupes from actual_nums
    dupes_dict = {}
    for key in nsv_dict:
        dupes_dict[key] = actual_nums[key]
    # print(dupes_dict)

    # To find dupes within the series, do a set check
    final_list = []
    dupes_list = []
    for num in actual_nums:
        if num not in final_list:
            final_list.append(num)
        else:
            # Get the duped value
            # dupes[list(reversed(actual_nums)).index(num)] = num
            dupes_list.append(num)
    # print(dupes_list)
    # Then need to find if the dupe occurs before the actual value or after
    # Has to differ by a certain threshold
    # Special case: What if both dupes are also identical?
    # Store al dupes into raw_dupes_dict
    raw_dupes_dict = {}
    for dupe in dupes_list:
        start_at = 0
        while True:
            try:
                dupe_idx = actual_nums.index(dupe, start_at)
            except ValueError:
                break
            else:
                raw_dupes_dict[dupe_idx] = dupe
                start_at = dupe_idx + 1

    # Check if dupe_idx (key) is close to dupe (value)
    # I think this is to avoid removing the original entry
    threshold = 5
    # dupes_dict = raw_dupes_dict.copy()
    # NOTE: This revealed that when entries are duped adjacently while entry number doesn't tally, the dupe is caught as a missing entry instead
    # print(raw_dupes_dict)
    for dupe_idx in raw_dupes_dict:
        dupe_val_check = abs(raw_dupes_dict[dupe_idx] % 1000 - dupe_idx)
        # Zero val occurs if a dupe lies next to the original entry
        if dupe_val_check > threshold:
            # dupes_dict.pop(dupe_idx)
            # Add this value to the combined dupes_dict
            dupes_dict[dupe_idx] = raw_dupes_dict[dupe_idx]
    # print(dupes_dict)

    # After finding all the dupes, remove them from the actual_nums
    count = 0
    for dupe_idx in dupes_dict:
        actual_nums.pop(dupe_idx - count)
        count += 1

    # GENERATE A LIST OF DIFFERENCES BETWEEN SEQUENTIAL ENTRIES
    # actual_deltas catches all the outliers
    actual_deltas = actual_nums[1:]
    # actual_deltas = [x - y for x,y in zip(actual_deltas, actual_nums[:-2])]
    # delta_series_nums = [actual - theory for actual, theory in zip(actual_nums, theory_nums)]
    # ALL OUTLIERS WILL BE DIFFERENT FROM '1'
    # outliers = [x for x in actual_deltas if x != 1]
    outliers = {'dupes':dupes_dict, 'missing_entries':{}}
    for x in range(len(actual_nums) - 1):
        delta_seq = actual_deltas[x] - actual_nums[x]
        if delta_seq != 1:
            outliers['missing_entries'][x] = delta_seq
    # print(outliers)
    # If the first entry is missing, then need to pick out separately
    # I could just throw in something quick to ensure that the first entry is present
    if actual_nums[0] % 1000 != 0:
        outliers['missing_entries'][0] = -10

    # Some of the missing entries have value 0. This is because they are actually dupes
    # Think it'd be easier to transfer them as the final step instead of trying to redo the workflow above.
    # I can safely remove the next entry, because it's a dupe. Regardless of first or second.
    # Delete that next entry
    # It worked
    indexes_to_switch = []
    for x in outliers['missing_entries']:
        if outliers['missing_entries'][x] == 0:
            outliers['dupes'][x] = actual_nums[x+1]
            indexes_to_switch.append(x)

    # I can't pop entries from a dict while it's in a loop. It returns a dict_length error or sth.
    for x in indexes_to_switch:
        outliers['missing_entries'].pop(x)

    return outliers

# Just put this under a function first
def scrape_num_names():
    # Handle SCP-000 which isn't listed
    scip_names = {}
    scip_nums = {}
    scip_links = {}
    outliers_all = {}
    sumchecks_all = {}
    # I think this is meant to be a nested list
    #many_series = []
    thous_dgt = 0
    # Not a true function but just to sequester this test kit away
    def series_link_testkit():
        test_list = driver.find_elements_by_xpath('//a[contains(@href, "scp-")]')
        test_series = [x for x in test_list if x.get_attribute('href').split('scp-')[1].isdigit() == True]
        len(test_list)
        len(test_series)
        test_series[500].get_attribute('href')
        for guy in test_series[225:240]:
            print(guy.get_attribute('href'))

    # thous_dgt determines the start
    for link in series_links[thous_dgt:]:
    # count = 0
    # while count < 1:
    #     count += 1
    #     link = series_links[thous_dgt]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # SCRAPING LOOP START
        print('Start ' + link + ' at ' + str(dt.datetime.now()))
        # Open the webpage of the SCP Series #
        driver.get(link)

        # Find all the hrefs first
        href_all = driver.find_elements_by_xpath("//a[@href]")
        # Find all hrefs containing three digits
        num_href = [href for href in href_all if type(re.search(r'\d\d\d', href.get_attribute('href'))) == re.Match]
        # Find all hrefs containing '#'
        hashtag_href = [href for href in num_href if type(re.search(r'#', href.get_attribute('href'))) == re.Match]
        # Find the scip numbers by taking inverse of hashtag_href
        series_hrefs = [href for href in num_href if href not in hashtag_href]
        # 1000th entry might be a link to the forums which may contain a 6-digit number
        # Filters out all hrefs with numbers
        series_nums = [int(re.sub("\D", "", href.get_attribute('href'))) for href in series_hrefs]
        # Only catch all the SCP entries which are 4-digit numbers. Can raise the threshold if they hit Series XI or something.
        series_nums = [number for number in series_nums if number < 10000]
        # Use the length of series_nums to limit series_text
        series_text = [href.find_element_by_xpath("..").text for href in series_hrefs[:len(series_nums)]]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # CHECK SERIES NUMS VS THEORY NUMS
        # Series I link ends with 's': http://www.scp-wiki.net/scp-series
        # Series I page starts at SCP-001, not SCP-000
        if link[-1] != 's':
            # Generate theory series
            theory_series_nums = gen_arith_seq(thous_dgt*1000, thous_dgt*1000 + 999, '')

        else:
            # Generate theory series
            theory_series_nums = gen_arith_seq(thous_dgt*1000, thous_dgt*1000 + 999, '')
            series_nums.insert(0, 0)
            series_text.insert(0, 'SCP-000')
            series_links.insert(0, 'http://www.scpwiki.com/scp-000')

        # Compare theory series against actual series
        series_sumcheck = sum(series_nums) - sum(theory_series_nums)
        # print('Delta between actual and theory is ' + str(series_sumcheck))
        outliers_dict = find_outliers(theory_series_nums, series_nums)
        print(outliers_dict)
        print(bool(outliers_dict['dupes']))
        if bool(outliers_dict['dupes']):
            for index in outliers_dict['dupes']:
                print('Removing index ' + str(index))
                try:
                    print('Popping dupes')
                    series_hrefs.pop(index)
                    series_nums.pop(index)
                    series_text.pop(index)
                except KeyError:
                    print('KeyError encountered.')
                except IndexError:
                    print('IndexError encountered.')

        scip_links[thous_dgt] = [href.get_attribute('href') for href in series_hrefs]
        scip_nums[thous_dgt] = series_nums
        scip_names[thous_dgt] = series_text
        outliers_all[thous_dgt] = outliers_dict
        sumchecks_all[thous_dgt] = series_sumcheck

        thous_dgt += 1
        print('End at ' + str(dt.datetime.now()))
        print('==============================')

    # Remove any extra elements that may arise from changing ads
    test_dfs = []
    for num in range(6):
        temp_df = pd.DataFrame(index=scip_nums[num][:1000], data=scip_names[num][:1000], columns=['Title'])
        # temp_df = pd.DataFrame(index=scip_nums[num][:1000], data=[scip_names[num][:1000], scip_hrefs[num][:1000]],
        #                        columns=['Title', 'Link'])
        temp_df['Link'] = scip_links[num][:1000]
        test_dfs.append(temp_df)

    scips_df = pd.concat(test_dfs)

    print('Start ' + link + ' at ' + str(dt.datetime.now()))
    # scips_df['Tags'] = scips_df['Link'].apply(lambda x: get_scp_tags(x))
    print('End at ' + str(dt.datetime.now()))
    #FIX topup_list_lengths()

    # Save this in an external file because it takes really long to get all the data.
    # On the next round, make sure I get every bit of data or metadata I'm looking for.
    folder_path = r"C:\Users\Julio Hong\Documents\GitHub\SCP Foundation\\"
    filename = folder_path + 'scp_df.xlsx'
    print('Exporting results to Excel')
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    scips_df.to_excel(writer, sheet_name='Sheet0')
    writer.save()
    writer.close()

folder_path = r"C:\Users\Julio Hong\Documents\GitHub\SCP Foundation\\"
filename = folder_path + 'scp_df.xlsx'
scips_df = pd.read_excel(filename, sheet_name='Sheet0', index_col=0)
# # scp_df.loc[:10,'Tags'] = scp_df.loc[:10,'Link'].apply(lambda x: get_scp_tags(x))

folder_path = r"C:\Users\Julio Hong\Documents\GitHub\SCP Foundation\\"
filename = folder_path + 'reobj_df.xlsx'
reobj_df = pd.read_excel(filename, sheet_name='Sheet0', index_col=0)
len(reobj_df.loc[reobj_df['Object_Class'] != 0].index)
acs_df = reobj_df.loc[reobj_df['Altv_Info'] != 0]
altv_ser = acs_df.loc[acs_df['Altv_Info'] != '{}', 'Altv_Info']

def scrape_list_to_df(input_df, start_val=2):
    # I'm trying to do this in a Pythonic manner. But I can't figure out how to make multiple rows the result of the apply function?
    # new_cols = ['Object_Class', 'Rating', 'Page_Tags', 'Num_of_Revn',
    #               'Last_revn_date', 'Discussion_count', 'Outgoing_SCPs', 'Languages']
    new_cols = list(input_df.columns)[3:]
    # col_order = scips_df.columns.to_list() + new_cols
    # scips_df = scips_df.reindex(columns=col_order)
    # I was going to replace it, but scraping only takes a bit more time
    # And it'll help me to check if the first run was accurate
    # The issue: I want apply-lambda to return multiple columns
    # start_val defaults to 2 because SCP-000 and SCP-001 don't have standard page formats
    other_df = input_df.iloc[start_val:,:]
    # temp is a nested list. Each list entry should correspond to a column
    # Learned from https://stackoverflow.com/a/27385043
    temp = list(zip(*other_df['Link'].map(sps.scrape_page)))
    try:
        for i, c in enumerate(new_cols): other_df[c] = temp[i]
    except Exception as e:
        logger = getLogger()
        logger.error('Encountered ' + repr(e))
        print('SPS Scrape error')
        return temp
    
    # # Add back the first two rows
    # other_df = other_df.reindex(index=range(6000))
    other_df = other_df.reindex(index=input_df.index)
    # other_df.loc[:1] = input_df.loc[:1]

    return other_df

# Not really a function yet
def explain_incompleteness(another_df):
    another_df = scips_df.copy()
    check_df = another_df != 'ERRORED'
    # Check which scips have any missing data.
    another_df['Completeness'] = check_df.all(axis='columns')
    # This doesn't really work because this seems to be the default title, so some articles keep this while non-existent ones also have this.
    # another_df.loc[another_df['Title'].str.contains('ACCESS DENIED')]
    # Categorise the causes of incompleteness. Can use test_df to help.
    # Find out which scips are incomplete.
    incomplete_df = check_df.loc[another_df['Completeness'] == False]
    causes_list = []
    # For each scip, find out which columns contain 'ERRORED'
    # Somewhat brutal
    for idx in incomplete_df.index:
        cause = list(incomplete_df.loc[idx, incomplete_df.loc[idx] == False].index)
        causes_list.append(cause)
    # Store this list of columns under 'Causes_of_Incompleteness'
    incomplete_df['Causes_of_incompleteness'] = causes_list
    # This returns all the counts
    causes_counts = incomplete_df.loc[:,'Causes_of_incompleteness'].value_counts()

    # # How to find the unwritten articles
    unwritten_df = incomplete_df[incomplete_df['Causes_of_incompleteness'].apply(lambda x: x != ['Object_Class'])]
    unwritten_list = list(unwritten_df.index)
    odd_obj_df = incomplete_df[incomplete_df['Causes_of_incompleteness'].apply(lambda x: x == ['Object_Class'])]
    odd_obj_list = [idx for idx in list(odd_obj_df.index) if idx not in unwritten_list]
    reobj_df = scips_df.loc[odd_obj_list]
    reobj_df.insert(4, 'Altv_Info', 0)
    return reobj_df

    # reobj_df.insert(5, 'Secondary_Class', 0)
    # reobj_df.insert(5, 'Containment_Class', 0)
    # idx_error_df = reobj_df.loc[idx_error_list]
    # no_such_elem_list = [x for x in reobj_df.index if x not in idx_error_list]
    # no_such_elem_df = reobj_df.loc[no_such_elem_list]
    # again_df = scrape_list_to_df(reobj_df[:10], start_val=0)


    # return another_df, causes_counts

# another_df = scips_df.copy()
# another_df, causes_count = explain_incompleteness(another_df)

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