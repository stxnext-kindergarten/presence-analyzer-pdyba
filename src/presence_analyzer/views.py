# -*- coding: utf-8 -*-
"""
Defines views.
"""
# pylint: disable=invalid-name

import calendar

from flask import redirect, abort, render_template, url_for

from presence_analyzer.main import app
from presence_analyzer.utils import jsonify, get_data, mean, group_by_weekday, \
    group_by_weekday_start_end

import logging
log = logging.getLogger(__name__)


@app.route('/')
def mainpage():
    """
    Renders mainpage
    """
    return redirect(url_for('presence_weekday_way'))


@app.route('/presence_weekday.html')
def presence_weekday_way():
    """
    Renders mainpage
    """
    return render_template('presence_weekday.html')


@app.route('/mean_time_weekday.html')
def mean_time_weekday_way():
    """
    Renders mainpage
    """
    return render_template('mean_time_weekday.html')


@app.route('/presence_start_end.html')
def presence_start_end_way():
    """
    Renders mainpage
    """
    return render_template('presence_start_end.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/', methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday(bar graph)
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/', methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday(circle graph)
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]
    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/', methods=['GET'])
@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)
    weekdays = group_by_weekday_start_end(data[user_id])
    result = []
    for i in weekdays:
        result.append([calendar.day_abbr[i], weekdays[i][0], weekdays[i][1]])
    return result
