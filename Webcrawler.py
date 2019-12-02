import time

import requests
import sqlite3 as sql
import sys
from datetime import datetime
from bs4 import BeautifulSoup, Tag


class Conference:

    def __init__(self):
        self.event = None
        self.name = None
        self.start = None
        self.end = None
        self.where = None
        self.deadline = None

    def add_info(self, info):

        if self.event is None:
            self.event = info

        elif self.name is None:
            self.name = info

        elif self.start is None:
            if len(info.split('-')) == 2:
                self.start = datetime.strptime(info.split('-')[0].strip(), "%b %d, %Y")
                self.end = datetime.strptime(info.split('-')[1].strip(), "%b %d, %Y")
            else:
                self.start = 'N/A'
                self.end = 'N/A'

        elif self.where is None:
            self.where = info

        elif self.deadline is None:
            self.deadline = info

    def __str__(self):

        return f'event = {self.event}\nname = {self.name}\nwhen = {self.start} - {self.end}\nwhere = {self.where}\ndeadline = ' \
            f'{self.deadline}\n'


connection = sql.connect('events.db')
cursor = connection.cursor()


def build_db():
    connection.execute("DROP TABLE IF EXISTS Events")
    connection.execute("CREATE TABLE Events(Event TEXT, Name TEXT, FirstDate DateTime, LastDate DateTime, Location TEXT, Deadline TEXT)");

    parameters = {'page': '1'}

    for page_num in range(1, 6):

        if page_num != 1:
            time.sleep(5)

        parameters['page'] = page_num

        r = requests.get('http://www.wikicfp.com/cfp/call?conference=computer%20science', params=parameters).text

        # print(r)

        soup = BeautifulSoup(r, 'lxml')
        # print(soup.prettify())

        # <table cellpadding="3" cellspacing="1" align="center" width="100%">
        test = soup.find('table', {'cellpadding': '3', 'cellspacing': '1', 'align': 'center', 'width': '100%'})


        data = test.find_all('td')

        # print(data)

        remove_links = []

        cur_info = Conference()

        iterator = 0

        for line in data:

            if iterator < 4:
                iterator += 1
                continue

            # if type(line.contents[0]) == NavigableString or type(line.contents[0]) == NavigableString:
            content = line.contents[0]

            if type(content) == Tag:

                if len(content.contents) == 0:
                    continue

                content = content.contents[0]

            cur_info.add_info(content)

            if (iterator - 3) % 5 == 0 and (iterator-4) != 0:
                remove_links.append(cur_info)

                cur_info = Conference()

            iterator += 1

        for conf in remove_links:
            connection.execute("INSERT INTO Events VALUES(?, ?, date(?), date(?), ?, ?)", (conf.event, conf.name, conf.start, conf.end, conf.where, conf.deadline))



    connection.commit()

def print_all(): 
    cursor.execute('SELECT * FROM Events')
    for evt in cursor.fetchall():
        print(evt)

def search(year, month):
    cursor.execute('SELECT * FROM Events WHERE strftime(\'%Y-%m\', FirstDate) = ? OR strftime(\'%Y-%m\', LastDate) = ?', (year + '-' + month, year + '-' + month))
    for evt in cursor.fetchall():
        print(evt)

def main():

    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'dbmake':
            build_db()
        elif sys.argv[1].lower() == 'all':
            print_all()
        elif sys.argv[1].lower() == 'search':
            if len(sys.argv) != 4:
                print("Search requires a year and month argument.")
            else:
                search(sys.argv[2], sys.argv[3])
        else:
            print("Invalid argument: " + sys.argv[1])
    else:
        print('Requires one of: dbmake, all, or search')

    connection.close()


if __name__ == '__main__':
    main()
