"""
PA1: Course Search Engine Part 1
Jingwen Lu
"""
# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg=invalid-name, redefined-outer-name, unused-argument, unused-variable

import queue
import json
import sys
import csv
import re
import bs4
import util


INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])


def get_html(requesting_url):
    '''
    Get actural url and html content

    Input: requesting_url
    Return: actual_url (str), html_content (str or None)
    '''

    requested = util.get_request(requesting_url)
    if requested is None:
        return None, None
    else:
        actural_url = util.get_request_url(requested)
        html_content = util.read_request(requested)
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8', errors='ignore')
    return actural_url, html_content


def get_new_urls(html_content):
    '''
    get all the url in the given html content

    Input: html_content
    Return: the urls
    '''

    soup = bs4.BeautifulSoup(html_content, 'html5lib')
    links = soup.find_all('a')
    hrefs = [link.get('href') for link in links]
    return hrefs


def update_index(word_lst, course_id, index_dic):
    '''
    put word into index dictionary and put corresponding course id into it.

    Input: word_lst, course_id
    Return: updated index_dic
    '''
    for word in word_lst:
        word_insensitive = word.lower()
        if word_insensitive in INDEX_IGNORE:
            continue
        else:
            if word_insensitive not in index_dic:
                index_dic[word_insensitive] = []
            if course_id not in index_dic[word_insensitive]:
                index_dic[word_insensitive].append(course_id)
    return index_dic


def get_course_code(info):
    '''
    get the course code

    Input: soup of course information
    Return: course_code, actual_title
    '''
    title_tag = info.find('p', attrs={'class': 'courseblocktitle'})

    if not title_tag or not title_tag.strong:
        course_code, actual_title = None, ''
    else:
        raw_title = title_tag.strong.text.strip()
        actual_title = raw_title.replace('\xa0', ' ')
        title_divide = actual_title.split()
        course_code = title_divide[0] + ' ' + title_divide[1]
        course_code = course_code.replace('.', '')
    return course_code, actual_title


def get_course_word_lst(info, actual_title):
    '''
    get the wordlist for the course

    Input: course info, course title
    Return: word_lst
    '''
    description_tag = info.find('p', attrs={'class': 'courseblockdesc'})
    if not description_tag:
        word_lst = []
    else:
        raw_info = description_tag.text.strip() + actual_title
        word_lst = re.findall(r'[a-zA-Z]\w*', raw_info)
    return word_lst


def find_index_in_page(soup, course_map, index_dic):
    '''
    get the course information and renew the dictionary of index

    Input: soup, course_map, index_dic
    Return: index_dic
    '''

    course_info = soup.find_all('div', attrs={'class': 'courseblock main'})

    for info in course_info:
        try:
            course_code, actual_title = get_course_code(info)
            if not course_code:
                continue
            word_lst = get_course_word_lst(info, actual_title)

            sequences = util.find_sequence(info)

            if course_code in course_map:
                course_id = course_map[course_code]
                index_dic = update_index(word_lst, course_id, index_dic)

            elif len(sequences) > 0:
                for sub_course in sequences:
                    sub_code, sub_title = get_course_code(sub_course)
                    if sub_code in course_map:
                        course_id = course_map[sub_code]
                        index_dic = update_index(
                            word_lst, course_id, index_dic)
                        word_lst_sub = get_course_word_lst(
                            sub_course, sub_title)
                        index_dic = update_index(
                            word_lst_sub, course_id, index_dic)
                    else:
                        continue

            else:
                continue

        except Exception as e:
            print('Here is an error:', e)
            continue
        
    return index_dic


def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index index.
    '''

    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    url_queue = queue.Queue()
    url_queue.put(starting_url)
    url_visited = set()

    with open(course_map_filename, 'r') as f:
        course_map = json.load(f)

    index_dic = {}

    while (len(url_visited) < num_pages_to_crawl) and (not url_queue.empty()):
        current_url = url_queue.get()
        actural_url, html_content = get_html(current_url)

        if actural_url is None or html_content is None:
            continue

        if isinstance(actural_url, bytes):
            actural_url = actural_url.decode('utf-8', errors='ignore')

        url_visited.update([current_url, actural_url])

        soup = bs4.BeautifulSoup(html_content, 'html5lib')
        index_dic = find_index_in_page(soup, course_map, index_dic)

        new_urls = get_new_urls(html_content)

        if not new_urls:
            continue

        for u in new_urls:
            if isinstance(u, bytes):
                u = u.decode('utf-8', errors='ignore')
            url = util.remove_fragment(u)
            if not util.is_absolute_url(url):
                url = util.convert_if_relative_url(actural_url, url)

            if url is None:
                continue
            if isinstance(url, bytes):
                url = url.decode('utf-8', errors='ignore')
            if util.is_url_ok_to_follow(url, limiting_domain
                                        ) and (url not in url_visited):
                url_queue.put(url)

    with open(index_filename, 'w', newline='') as f:
        output = csv.writer(f, delimiter='|')
        for word in index_dic.keys():
            course_ids = index_dic[word]
            for course_id in course_ids:
                output.writerow([course_id, word])
    return


if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 100
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
