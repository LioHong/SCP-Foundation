# -*- coding: utf-8 -*-
"""
Filename: scp_page_scraper.py
Date created: Sat Aug 29 19:45:18 2020
@author: Julio Hong
Purpose: 
Steps: 
"""

from selenium import webdriver
import pandas as pd
import datetime as dt
from random import randint
import re
from selenium.common.exceptions import NoSuchElementException
from logging import getLogger

# To adjust the dataframe appearance
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 200)

driver = webdriver.Chrome(r"C:\Users\Julio Hong\chromedriver_win32\chromedriver.exe")
test_link = 'http://www.scpwiki.com/scp-' + str(randint(0, 5999))

# Ideally I'll go to one page and then run all these functions at one shot.
# Then I need to slot them into the scp_df somehow
# So I should also be able to load a single driver for each one. Maybe do get_lang_interwiki because need to change the frame.

# Overall function
# Set up to return 'ERRORED' instead of throwing an exception
# But I do want to check what kind of error we're dealing with.
def scrape_page(link):
    print(link)
    driver.get(link)

    # Check if article exists
    discuss_count = get_scp_discussion()
    if discuss_count != 'ERRORED':
        obj_class_text = get_scp_obj_class()
        # cont_class_text = get_scp_cont_class()
        # sec_class_text = get_scp_sec_class()

        rating = get_scp_rating()
        page_tags = get_scp_tags()
        num_of_revn, last_revn_dt_obj = get_rev_data()
        outgoing_scips = get_outgoing_scips(link)
        # altv_info = 0
        altv_info = det_altv_classification()

        # Every other bit of metadata can be found except object class
        if obj_class_text == 'ERRORED':
            # Find collapsible because one line
            try:
                # Then find object class because also one line
                # One branch to find object class within collapsible
                click_collapsible()
                obj_class_text = get_scp_obj_class()
                # altv_info = det_altv_classification()

                # if obj_class_text == 'ERRORED':
                #     # Find altv classification within collapsible
                #     altv_info = det_altv_classification()

            except:
                print('Collapsible not found')
                # Find altv classification
                # altv_info = det_altv_classification()
            # Replace the 'ERRORED' value with 0 so as to not trigger the error-check
            if obj_class_text == 'ERRORED':
                obj_class_text = 0

        # if obj_class_text == 'ERRORED' and cont_class_text == 'ATTEMPTED':
        #     try:
        #         click_collapsible()
        #         obj_class_text = get_scp_obj_class()
        #         # cont_class_text = get_scp_cont_class()
        #         # sec_class_text = get_scp_sec_class()
        #     except:
        #         print('Collapsible not found')


        # Last because need to change driver frame
        langs = get_lang_interwiki()
        # scraped_list = [obj_class_text, cont_class_text, sec_class_text, rating,
        #             page_tags, num_of_revn, last_revn_dt_obj, discuss_count, outgoing_scips, langs]
        # altv_info = 0
        scraped_list = [obj_class_text, altv_info, rating, page_tags, num_of_revn,
                        last_revn_dt_obj, discuss_count, outgoing_scips, langs]

    else:
        # The article is unwritten/deleted
        scraped_list = ['UNWRITTEN', 0, 0, 0, 0, 0, 0, 0, 0]

    # Just to keep track of errors
    if 'ERRORED' in scraped_list:
        print('Error present')
    return scraped_list

# Quick function to check what kind of errors I get for object, containment and secondary class i.e. diagnostic
# Also might try running multiple consoles
# def check_scp_class_errors(input_df, start_val=0, end_val=-1):
def check_scp_class_errors(input_df):
    def get_obj_cont_sec(link):
        try:
            print(link)
            driver.get(link)
            # obj_class_text = get_scp_obj_class()
            # cont_class_text = get_scp_cont_class()
            # sec_class_text = get_scp_sec_class()

            obj_class = driver.find_element_by_xpath("//*[contains(text(), 'Object Class:')]")
            obj_class_text = obj_class.find_element_by_xpath('..').text.split(': ')[1]

            cont_class = driver.find_element_by_xpath("//*[contains(text(), 'Containment Class:')]")
            cont_class_text = obj_class.find_element_by_xpath('..').text.split(':')[1]

            sec_class = driver.find_element_by_xpath("//*[contains(text(), 'Secondary Class:')]")
            sec_class_text = obj_class.find_element_by_xpath('..').text.split(':')[1]

            return obj_class_text, cont_class_text, sec_class_text
        # https://www.loggly.com/blog/exceptional-logging-of-exceptions-in-python/
        # except Exception:
        #     logger = getLogger()
        #     logger.exception("Fatal error in main loop")
        # https://stackoverflow.com/questions/4690600/python-exception-message-capturing
        except Exception as e:
            logger = getLogger()
            logger.error('Encountered ' + repr(e))
            return repr(e).split('(')[0], 'placeholder1', 'placeholder2'

    new_cols = ['Object_Class', 'Containment_Class', 'Secondary_Class']
    # other_df = input_df.loc[start_val:end_val,:]
    # I can just do loc for input_df
    other_df = input_df.copy()
    temp = list(zip(*other_df['Link'].map(get_obj_cont_sec)))
    print(temp)
    for i, c in enumerate(new_cols): other_df[c] = temp[i]
    print('DF done')
    return other_df


# Rating
def get_scp_rating():
    try:
        rating = driver.find_element_by_class_name("rate-points").text.split(' ')[-1]
        return rating
    except:
        return 'ERRORED'

# Languages
def get_lang_interwiki():
    try:
        driver.switch_to.frame(driver.find_element_by_class_name("scpnet-interwiki-frame"))
        interwiki = driver.find_elements_by_class_name("interwiki__entry")
        languages = []
        for lang in interwiki:
            languages.append(lang.text)
        return languages
    except:
        return 'ERRORED'

# Page revision
# Date last revised
def get_rev_data():
    try:
        revision_data = driver.find_element_by_id("page-info").text
        num_of_revn, last_revn_datetime = revision_data.split(', last edited: ')
        num_of_revn = int(num_of_revn.split('page revision: ')[1])
        last_revn_datetime = last_revn_datetime.split(' (')[0]
        last_revn_dt_obj = dt.datetime.strptime(last_revn_datetime, '%d %b %Y, %H:%M')
        return num_of_revn, last_revn_dt_obj
    except:
        return 'ERRORED', 'ERRORED'

# Tags
def get_scp_tags():
    try:
        hrefs_all = driver.find_elements_by_xpath("//a[@href]")
        page_tags = [elem.get_attribute('href').split('/')[-1].split('#')[0]
                     for elem in hrefs_all if 'page-tags' in elem.get_attribute('href')]
        return page_tags
    except:
        return 'ERRORED'

# Object Class
# Can get from tags?
# get_scp_tags('http://www.scpwiki.com/scp-2213')
# get_scp_tags(test_link)
# Just get it from the element because it can be weird sometimes
def get_scp_obj_class(debug=False):
    try:
        obj_class = driver.find_element_by_xpath("//*[contains(text(), 'Object Class:')]")
        # while obj_class.text == 'Object Class:':
        while obj_class.text.upper() == 'OBJECT CLASS:':
            # Debug
            if debug:
                print('OCT - ' + obj_class.text)
            obj_class = obj_class.find_element_by_xpath('..')
        obj_class_text = obj_class.text.split(': ')[1]
        return obj_class_text
    except Exception as e:
        if debug:
            logger = getLogger()
            logger.error('Encountered ' + repr(e))
        return 'ERRORED'


def get_scp_cont_class():
    try:
        cont_class = driver.find_element_by_xpath("//*[contains(text(), 'Containment Class:')]")
        cont_class_text = obj_class.find_element_by_xpath('..').text.split(':')[1]
        return cont_class_text
    except:
        return 'ATTEMPTED'


def get_scp_sec_class():
    try:
        sec_class = driver.find_element_by_xpath("//*[contains(text(), 'Secondary Class:')]")
        sec_class_text = obj_class.find_element_by_xpath('..').text.split(':')[1]
        return sec_class_text
    except:
        return 'ATTEMPTED'

# Number of discussion posts
def get_scp_discussion():
    try:
        discuss_count = int(driver.find_element_by_id("discuss-button").text.split('Discuss (')[1][:-1])
        return discuss_count
    except NoSuchElementException:
        return 'ERRORED'

# Links to other SCPs
def get_outgoing_scips(link):
    try:
        own_scp_num = link.split('-')[-1]
        hrefs_all = driver.find_elements_by_xpath("//a[@href]")
        scip_links = [elem for elem in hrefs_all if 'scp-' in elem.get_attribute('href')]
        # 3 digits to account for Series I.
        other_scips = [href for href in scip_links if type(re.search(r'\d\d\d', href.get_attribute('href'))) == re.Match]
        # Check if own SCP-# is inside
        non_adj_scips = [href for href in other_scips if own_scp_num not in href.get_attribute('href')]
        # Then check if SCP-# +1 or -1 is inside
        non_adj_scips = [href for href in non_adj_scips if str(int(own_scp_num)+1) not in href.get_attribute('href')]
        non_adj_scips = [href for href in non_adj_scips if str(int(own_scp_num)-1) not in href.get_attribute('href')]
        if not non_adj_scips:
            # print('No outgoing links to other SCPs.')
            return None
        else:
            outgoing_scips = [href.get_attribute('href').split('-')[-1] for href in non_adj_scips]
            return outgoing_scips
    except:
        return 'ERRORED'


def det_altv_classification():
    # Just fill this with details whenever possible. Use a dict.
    disrupt_class = find_elem_by_text('Disruption Class:')
    site_assigned = find_elem_by_text('Assigned Site:')
    site_responsible = find_elem_by_text('Site Responsible:')
    contain_class = find_elem_by_text('Containment Class:')
    altv_info = {}

    def scrape_more_metadata(keys_list, error_val='ERRORED'):
        output_dict = dict.fromkeys(keys_list, 0)
        for entry in keys_list:
            output_dict[entry] = find_elem_by_text(entry, error_val)
        return output_dict

    # If Disruption class is present, ACS is used.
    if disrupt_class != 'ERRORED':
        # Some articles use the new classification system found here: http://www.scp-wiki.net/classification-committee-memo
        # Detailed here: http://scp-wiki.wikidot.com/anomaly-classification-system-guide

        acs_keys = ['Containment Class:', 'Secondary Class:', 'Disruption Class:', 'Risk Class:']
        # acs_dict = dict.fromkeys(acs_info, 0)
        # for acs_class in acs_keys:
        #     acs_dict[acs_class] = find_elem_by_text(acs_class)
        # altv_info.update(acs_dict)
        acs_dict = scrape_more_metadata(acs_keys, 'None')
        # clear = driver.find_element_by_class_name('clearance')
        try:
            clear = driver.find_element_by_xpath('//*[contains(@class, "clearance")]')
            acs_dict['Clearance'] = clear.find_element_by_xpath('..').text
        except:
            print('Clearance not found')

        altv_info.update(acs_dict)
    elif contain_class != 'ERRORED':
        altv_info['Containment'] = contain_class

    # # More info, and then leads into Midgard-style
    # # Formatting uses a table, hard to scrape
    # if site_assigned != 'ERRORED':
    #     more_keys = ['Assigned Site:', 'Site Director:', 'Research Head:', 'Assigned Task Force:']
    #     more_dict = scrape_more_metadata(more_keys)
    #
    #     # Check for Midgard-style


    # Atzak-style
    if site_responsible != 'ERRORED':
        atzak_keys = ['Site Responsible:', 'Director:', 'Research Head:', 'Assigned Task Force:']
        atzak_dict = scrape_more_metadata(atzak_keys)
        level = driver.find_element_by_xpath('//*[contains(@class, "leveltext")]')
        atzak_dict['Clearance'] = level.text

        altv_info.update(atzak_dict)

    return altv_info


# There's also another classification format. I'll call it Atzak style based on SCP=3000
# 'Object Class:' apparently still works on this?
more_info = ['Assigned Site', 'Site Director', 'Research Head', 'Assigned Task Force']
atzak_info = ['Clearance Level', 'Site Responsible', 'Director', 'Research Head', 'Assigned Task Force']
# atzak_info = ['Clearance Level'] + more_info
# Now there's Midgard style, which seems to encompass Atzak style.
# midgard_info = ['Containment Class', 'Object Class', 'Clearance Level', 'Assigned Site', 'Site Director', 'Research Head', 'Assigned Task Force']
midgard_info = ['Containment Class', 'Object Class', 'Clearance Level'] + more_info

# Check if there are any tales involved. Not sure how to handle this. Maybe check which links exist between entries?
# The method of getting these is quite different from the rest though, so no need to include.

# Maybe also check if it's been declassified. Apparently the hub just links back to Reddit posts.
declass_link = 'http://www.scpwiki.com/scpdeclassified'


def click_collapsible():
    # By itself not very informative. But can check if it coincides with unscraped articles.
    colaps = driver.find_elements_by_xpath('//a[contains(@class, "collapsible")]')
    if bool(colaps):
        print('Collapsible element present.')
        # print(colaps[0].text)
        # Usually the first element is the 'Security Clearance' warning button
        colaps[0].click()

def find_elem_by_text(text, error_val='ERRORED', debug=False):
    try:
        elem = driver.find_element_by_xpath("//*[contains(text(), '" + text + "')]")
        parent = elem.find_element_by_xpath('..')
        parent_text = parent.text.split(':')[1]
        return parent_text
    except Exception as e:
        if debug:
            logger = getLogger()
            logger.error('Encountered ' + repr(e))
        return error_val
