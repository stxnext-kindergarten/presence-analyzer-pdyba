# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""
import urllib
import csv

from datetime import datetime
from json import dumps
from functools import wraps
from itertools import chain

from lxml import etree

from flask import Response

from presence_analyzer.main import app

import logging

log = logging.getLogger(__name__)
# pylint: disable=invalid-name, missing-docstring


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """

    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )

    return inner


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def group_by_weekday_start_end(items):
    """
    Groups presence entries by weekday.
    """
    result = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    for date in items:
        start = str(items[date]['start']).split(':')
        end = str(items[date]['end']).split(':')
        start_2 = [1, 1, 1, int(start[0]), int(start[1]), int(start[2])]
        end_2 = [1, 1, 1, int(end[0]), int(end[1]), int(end[2])]
        if not result[date.weekday()]:
            result[date.weekday()] = [start_2, end_2]
        else:
            for i in range(5):
                start_2[i] = (start_2[i] + (result[date.weekday()])[0][i]) / 2
                end_2[i] = (end_2[i] + (result[date.weekday()])[1][i]) / 2
            result[date.weekday()] = [start_2, end_2]
    for day in result:
        if not result[day]:
            result[day] = [[1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]]
    return result


def user(uid):
    users = {}
    xml = urllib.urlopen('http://sargo.bolt.stxnext.pl/users.xml')
    tree = etree.parse(xml)
    root = tree.getroot()
    server = root.find('server')
    server_url = server.find('protocol').text + "://" + server.find('host').text
    for user in root.find('users'):
         users[int(user.get('id'))] = {'name': user.find('name').text,'image_url': server_url + user.find('avatar').text}
    return users[uid]
