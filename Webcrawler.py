import requests
from bs4 import BeautifulSoup, Tag


class Conference:

    def __init__(self):
        self.event = None
        self.name = None
        self.when = None
        self.where = None
        self.deadline = None

    def add_info(self, info):

        if self.event is None:
            self.event = info

        elif self.name is None:
            self.name = info

        elif self.when is None:
            self.when = info

        elif self.where is None:
            self.where = info

        elif self.deadline is None:
            self.deadline = info

    def __str__(self):

        return f'event = {self.event}\nname = {self.name}\nwhen = {self.when}\nwhere = {self.where}\ndeadline = ' \
            f'{self.deadline}\n'


def main():

    r = requests.get('http://www.wikicfp.com/cfp/call?conference=computer%20science').text

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

        print(conf)

    pass


if __name__ == '__main__':
    main()
