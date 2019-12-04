"""
Basic web scraper that scrapes the WikiCFP conference calendar and pushes the data to a database
"""

import time

import requests
import sqlite3 as sql
import sys
from datetime import datetime
from bs4 import BeautifulSoup, Tag


class Conference:
    """
    Class used to hold the info of a conference before insertion into database
    """

    def __init__(self):
        self.event = None
        self.name = None
        self.start = None
        self.end = None
        self.where = None
        self.deadline = None

    def add_info(self, info):
        """
        Function that takes a piece of info, and adds it to the appropriate parameter
        :param info: A string that represents data for the conference
        """

        if self.event is None:  # If the event is not set, sets it to the info
            self.event = info

        elif self.name is None:  # If the event name is not set, sets it to the info
            self.name = info

        elif self.start is None:  # If the event start is not set
            if len(info.split('-')) == 2:  # Splits the date into the start and end dates, and sets them
                self.start = datetime.strptime(info.split('-')[0].strip(), "%b %d, %Y")
                self.end = datetime.strptime(info.split('-')[1].strip(), "%b %d, %Y")
            else:  # Otherwise, set both to N/A
                self.start = 'N/A'
                self.end = 'N/A'

        elif self.where is None:  # If the event location is not set, sets it to the info
            self.where = info

        elif self.deadline is None:  # If the event deadline is not set, sets it to the info
            self.deadline = info

    @property
    def __str__(self):
        """
        Sets the string representation of a conference
        :return: The string representing the conference
        """

        # Returns a string that shows all fields from the conference class
        return f'event = {self.event}\nname = {self.name}\nwhen = {self.start} - {self.end}\nwhere = {self.where}\n' \
               f'deadline = {self.deadline}\n'


# Connect to the database
connection = sql.connect('events.db')
cursor = connection.cursor()


def build_db():
    """
    Function that builds a database using information retrieved from the WikiCFP web calender
    """

    connection.execute("DROP TABLE IF EXISTS Events")  # Deletes any existing data
    connection.execute("CREATE TABLE Events(Event TEXT, Name TEXT, FirstDate DateTime, LastDate DateTime, "
                       "Location TEXT, Deadline TEXT)")  # Recreates table after deleting old table

    parameters = {'page': '1'}  # Sets parameters for get request

    for page_num in range(1, 6):  # For the first 5 pages

        if page_num != 1:  # If this is not the first request
            time.sleep(5)  # Waits 5 seconds before continuing

        parameters['page'] = page_num  # Sets the page number to get

        # Uses the requests library to send a get request to retrieve the requested page of the calender
        r = requests.get('http://www.wikicfp.com/cfp/call?conference=computer%20science', params=parameters).text

        soup = BeautifulSoup(r, 'lxml')  # Parses the webpage into lxml

        # Finds the start of the calandar using its unique table attributes, as it does not have a tag
        test = soup.find('table', {'cellpadding': '3', 'cellspacing': '1', 'align': 'center', 'width': '100%'})

        data = test.find_all('td')  # Finds the table

        conferences = []  # List of conferences

        cur_info = Conference()  # Creates new empty conference to be populated

        iterator = 0
        for line in data:  # For each line in the table

            if iterator < 4:  # Skips the first 4 lines, as it does not contain any useful data
                iterator += 1
                continue

            content = line.contents[0]  # Gets the content of the line

            if type(content) == Tag:  # If the line contains a html tag

                if len(content.contents) == 0:  # If the value in the tag is 0, skips line
                    continue

                content = content.contents[0]  # Sets the content to be the content of the tag

            cur_info.add_info(content)  # Adds the content to the current conference object

            if (iterator - 3) % 5 == 0 and (iterator-4) != 0:  # Every 5 lines is a full conference entry

                conferences.append(cur_info)  # Adds conference info to the array

                cur_info = Conference()  # Sets current conference to a new conference

            iterator += 1  # Increases iterator

        for conf in conferences:  # For each conference

            # Inserts conference into database
            connection.execute("INSERT INTO Events VALUES(?, ?, date(?), date(?), ?, ?)",
                               (conf.event, conf.name, conf.start, conf.end, conf.where, conf.deadline))

    connection.commit()  # Commits the database insertions to the database


def print_all():
    """
    Prints every conference info from the database
    """
    cursor.execute('SELECT * FROM Events')  # Selects every event
    for evt in cursor.fetchall():  # For each selected event
        print(evt)  # Prints event


def search(year, month):
    """
    Searches for events within a given date range
    :param year: The year to search for
    :param month: The month to search for
    """
    # Selects all events where the start date or end date fall within the given year and month
    cursor.execute('SELECT * FROM Events WHERE '
                   'strftime(\'%Y-%m\', FirstDate) = ? OR strftime(\'%Y-%m\', LastDate) = ?',
                   (year + '-' + month, year + '-' + month))
    for evt in cursor.fetchall():  # For each selected event
        print(evt)  # Prints event


def main():
    """
    Main class that reads in args, and either populates a database with conference events, or returns selected
    conferences
    """

    if len(sys.argv) > 1:  # If there are more than 1 arguments
        if sys.argv[1].lower() == 'dbmake':  # If the command is to build the database
            build_db()  # Builds the database
        elif sys.argv[1].lower() == 'all':  # If the command is to print all events
            print_all()  # Prints all events
        elif sys.argv[1].lower() == 'search':  # If the argument is to search for a given month
            if len(sys.argv) != 4:  # If there are not 4 args
                print("Search requires a year and month argument.")  # Displays error message
            else:
                search(sys.argv[2], sys.argv[3])  # Searches for the given month and year
        else:
            print("Invalid argument: " + sys.argv[1])  # Prints error message
    else:
        print('Requires one of: dbmake, all, or search')  # Prints error message

    connection.close()  # Closes the connection


if __name__ == '__main__':
    main()
