'''
Course search engine: search

Jingwen Lu
'''

from math import radians, cos, sin, asin, sqrt, ceil
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course_information.sqlite3')


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is list of strings
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enrollment is a pair of integers
      - walking_time is an integer
      - building_code ia string
      - terms is a list of strings string: ["quantum", "plato"]

    Returns a pair: an ordered list of attribute names and a list the
     containing query results.  Returns ([], []) when the dictionary
     is empty.
    '''

    assert_valid_input(args_from_ui)
    
    if not args_from_ui:
        return ([], [])


    def get_output_type(args_from_ui):
        '''
        get the output type based on the arguments
        INPUT: args_from_ui
        RETURN: number of groups of output 
        '''
        filters_requiring_meetings = {"day", "enrollment", "time_start", "time_end"}
        filters_requiring_walk = {"building_code", "walking_time"}

        if filters_requiring_walk & args_from_ui.keys():
            return 3
        elif filters_requiring_meetings & args_from_ui.keys():
            return 2
        else:
            return 1
    

    def get_output_headers(args_from_ui):
        '''
        get the output headers based on the arguments
        INPUT: args_from_ui
        RETURN: list of headers
        '''
        headers = [
            ["dept", "course_num", "title"],
            ["section_num", "day", "time_start", "time_end","enrollment"],
            ["building_code","walking_time"]]
        
        output_type = get_output_type(args_from_ui)
        return [header for line in headers[:output_type] for header in line]


    def get_select(args_from_ui):
        '''
        get fragments after "SELECT"
        INPUT: args_from_ui
        RETURN: string that can be put into query after SELECT
        '''
        select_term_group = [
            ["courses.dept", "courses.course_num", "courses.title"],
            ["sections.section_num", "meetings.day", "meetings.time_start", "meetings.time_end","sections.enrollment"],
            ["sections.building_code","time_between(loc_a.lon, loc_a.lat, loc_b.lon, loc_b.lat) AS walking_time"]
            ]
        
        output_type = get_output_type(args_from_ui)
        select_terms = [term for line in select_term_group[:output_type] for term in line]
        return "SELECT " + ", ".join(select_terms)
    

    def get_from_join(args_from_ui):
        '''
        get fragments after "FROM" and "JOIN"
        INPUT: args_from_ui
        RETURN: tuple with string that can be put into query after FROM and JOIN
        '''
        output_type = get_output_type(args_from_ui)

        target_building = args_from_ui.get('building_code', '') if output_type == 3 else ''

        join_table_groups = [
            [("catalog_index AS catalog ON catalog.course_id = courses.course_id")],
            [("sections AS sections ON sections.course_id = courses.course_id"), 
             ("meeting_patterns AS meetings ON sections.meeting_pattern_id = meetings.meeting_pattern_id")],
            [("gps AS loc_a on loc_a.building_code = sections.building_code"), 
             (f"gps AS loc_b ON loc_b.building_code='{target_building}'")]
            ] 

        from_expression = " FROM courses AS courses"

        join_terms = [term for line in join_table_groups[:output_type] for term in line]
        join_expression = " JOIN " + " JOIN ".join(join_terms)

        return from_expression  + join_expression
  

    def get_where(args_from_ui):
        '''
        get fragments after "WHERE"
        INPUT: args_from_ui
        RETURN: string that can be put into query after WHERE, where_value as parameters,
                and an optional HAVING clause
        '''

        where_parts = []
        where_values = []
        for col, value in args_from_ui.items():
            
            if col == "enrollment":
                where_parts.append(f"sections.enrollment BETWEEN ? AND ?")
                where_values.extend(value)
            elif col == "terms":
                placeholders = ','.join('?' for _ in value)
                where_parts.append(f"catalog.word IN ({placeholders})")
                where_values.extend(value)
            elif col == "day":
                placeholders = ','.join('?' for _ in value)
                where_parts.append(f"meetings.day IN ({placeholders})")
                where_values.extend(value)
            elif col == "time_start":
                where_parts.append(f"meetings.time_start >= ?")
                where_values.append(value)
            elif col == "time_end":
                where_parts.append(f"meetings.time_end <= ?")
                where_values.append(value)
            elif col == "walking_time":
                where_parts.append(f"time_between(loc_a.lon, loc_a.lat, loc_b.lon, loc_b.lat) <= ?")
                where_values.append(value)
            elif col == "building_code":
                pass
            else:
                where_parts.append(f"{col} = ?")
                where_values.append(value)
        having_clause = ""
        if "terms" in args_from_ui:
            having_clause = " HAVING COUNT(DISTINCT catalog.word) = ?"
            where_values.append(len(args_from_ui["terms"]))
        return "WHERE " + " AND ".join(where_parts), where_values, having_clause


    def get_group_by(args_from_ui):
        '''
        get the group by clause
        INPUT: args_from_ui
        RETURN: string that can be put into query after GROUP BY
        '''
        output_type = get_output_type(args_from_ui)
        if output_type <= 1:
            return " GROUP BY courses.title"
        return " GROUP BY courses.title, sections.section_num"


    conn = sqlite3.connect(DATABASE_FILENAME)
    cur = conn.cursor()
    conn.create_function('time_between', 4, compute_time_between)

    where_query, where_values, having_clause = get_where(args_from_ui)
    query = f"""{get_select(args_from_ui)} {get_from_join(args_from_ui)} {where_query} {get_group_by(args_from_ui)} {having_clause}"""
    print(query)
    print(where_values)
    results = cur.execute(query,where_values).fetchall()
    print("results",results)
    headers = get_output_headers(args_from_ui)
    print("headers",headers)
    return headers, results


########### auxiliary functions #################
########### do not change this code #############

def assert_valid_input(args_from_ui):
    '''
    Verify that the input conforms to the standards set in the
    assignment.
    '''

    assert isinstance(args_from_ui, dict)

    acceptable_keys = set(['time_start', 'time_end', 'enrollment', 'dept',
                           'terms', 'day', 'building_code', 'walking_time'])
    assert set(args_from_ui.keys()).issubset(acceptable_keys)

    # get both buiding_code and walking_time or neither
    has_building = ("building_code" in args_from_ui and
                    "walking_time" in args_from_ui)
    does_not_have_building = ("building_code" not in args_from_ui and
                              "walking_time" not in args_from_ui)

    assert has_building or does_not_have_building

    assert isinstance(args_from_ui.get("building_code", ""), str)
    assert isinstance(args_from_ui.get("walking_time", 0), int)

    # day is a list of strings, if it exists
    assert isinstance(args_from_ui.get("day", []), (list, tuple))
    assert all([isinstance(s, str) for s in args_from_ui.get("day", [])])

    assert isinstance(args_from_ui.get("dept", ""), str)

    # terms is a non-empty list of strings, if it exists
    terms = args_from_ui.get("terms", [""])
    assert terms
    assert isinstance(terms, (list, tuple))
    assert all([isinstance(s, str) for s in terms])

    assert isinstance(args_from_ui.get("time_start", 0), int)
    assert args_from_ui.get("time_start", 0) >= 0

    assert isinstance(args_from_ui.get("time_end", 0), int)
    assert args_from_ui.get("time_end", 0) < 2400

    # enrollment is a pair of integers, if it exists
    enrollment_val = args_from_ui.get("enrollment", [0, 0])
    assert isinstance(enrollment_val, (list, tuple))
    assert len(enrollment_val) == 2
    assert all([isinstance(i, int) for i in enrollment_val])
    assert enrollment_val[0] <= enrollment_val[1]


def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return int(ceil(mins))


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    header = []

    for i in cursor.description:
        s = i[0]
        if "." in s:
            s = s[s.find(".")+1:]
        header.append(s)

    return header
