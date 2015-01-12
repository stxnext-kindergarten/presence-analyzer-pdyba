# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
# pylint: disable=maybe-no-member, too-many-public-methods, missing-docstring,
# pylint: disable=unused-import
import calendar
import datetime
import json
import os.path
import unittest

from presence_analyzer import main, utils, views


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

# pylint: disable=maybe-no-member, too-many-public-methods, missing-docstring,

class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        resp = self.client.get('/api/v1/presence_weekday/10')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(data), 8, msg="Week has exactly 7 days")
        self.assertEquals(
            data,
            [
                ["Weekday", "Presence (s)"],
                ["Mon", 0],
                ["Tue", 30047],
                ["Wed", 24465],
                ["Thu", 23705],
                ["Fri", 0],
                ["Sat", 0],
                ["Sun", 0],
            ],
        )

    def test_presence_start_end_view(self):
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        print data
        self.assertEquals(
            data,
            [
                [u'Mon', [1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                [u'Tue', [1, 1, 1, 9, 39, 5], [1, 1, 1, 17, 59, 52]],
                [u'Wed', [1, 1, 1, 9, 19, 52], [1, 1, 1, 16, 7, 37]],
                [u'Thu', [1, 1, 1, 10, 48, 46], [1, 1, 1, 17, 23, 51]],
                [u'Fri', [1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                [u'Sat', [1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                [u'Sun', [1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                ],
        )
        self.assertEqual(len(data), 8, msg="Week has exactly 7 days")
        self.assertEquals(
            data,
            [
                ["Weekday", "Presence (s)"],
                ["Mon", 0],
                ["Tue", 30047],
                ["Wed", 24465],
                ["Thu", 23705],
                ["Fri", 0],
                ["Sat", 0],
                ["Sun", 0],
            ],
        )


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5),
            )

    def test_group_by_weekday_start_end(self):
        data = utils.get_data()
        result = utils.group_by_weekday_start_end(data[10])
        self.assertEquals(
            result,
            {
                0: [[1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                1: [[1, 1, 1, 9, 39, 5], [1, 1, 1, 17, 59, 52]],
                2: [[1, 1, 1, 9, 19, 52], [1, 1, 1, 16, 7, 37]],
                3: [[1, 1, 1, 10, 48, 46], [1, 1, 1, 17, 23, 51]],
                4: [[1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                5: [[1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                6: [[1, 1, 1, 12, 0, 0], [1, 1, 1, 12, 0, 0]],
                }
        )

    def test_group_by_weekday(self):
        data = utils.get_data()
        weekdays = data[10]
        self.assertEquals(
            utils.group_by_weekday(weekdays),
            [
                [],
                [30047],
                [24465],
                [23705],
                [],
                [],
                [],
                ],
            msg="group by weekday error test case 1",
            )
        weekdays_2 = data[11]
        self.assertEquals(
            utils.group_by_weekday(weekdays_2),
            [
                [24123],
                [16564],
                [25321],
                [22969, 22999],
                [6426],
                [],
                [],
                ],
            msg="group by weekday error test case 2",
            )

    def test_seconds_since_midnight(self):
        good_times = [
            [datetime.time(0, 1, 11), 71],
            [datetime.time(11, 11, 11), 40271],
            [datetime.time(23, 59, 59), 86399],
            [datetime.time(17, 31, 51), 63111],
            [datetime.time(6, 0, 59), 21659],
            ]
        for tim in good_times:
            self.assertEquals(utils.seconds_since_midnight(tim[0]),
                              tim[1])
        # BAD times:
        with self.assertRaises(ValueError):
            self.assertEquals(datetime.time(25, 25, 25), 91525,
                              msg='MidTime: over 24h day time')
            self.assertEquals(datetime.time(-1, -25, -25), 91525,
                              msg='MidTime: minus day time')

    def test_interval(self):
        # GOOD:
        self.assertEquals(
            utils.interval(
                datetime.time(9, 1, 23),
                datetime.time(17, 1, 23),
            ),
            28800,
            msg="interval err 1",
        )
        self.assertEquals(
            utils.interval(
                datetime.time(0, 1, 1),
                datetime.time(0, 11, 1),
            ),
            600,
            msg="interval err 2",
        )
        self.assertEquals(
            utils.interval(
                datetime.time(0, 0, 0),
                datetime.time(23, 59, 59),
            ),
            86399,
            msg="interval err 3",
        )
        # BAD:
        self.assertEquals(
            utils.interval(
                datetime.time(3, 0, 0),
                datetime.time(1, 0, 0),
                ),
            -7200,
            msg="interval err 4 wrong order start-end",
        )
        self.assertEquals(
            utils.interval(
                datetime.time(1, 0, 0),
                datetime.time(3, 0, 0),
            ),
            7200,
            msg="interval err 4 wrong order start-end",
        )

    def test_mean(self):
        data = utils.get_data()
        weekdays = utils.group_by_weekday(data[10])
        result = [
            (calendar.day_abbr[weekday], utils.mean(intervals))
            for weekday, intervals in enumerate(weekdays)
        ]
        self.assertEquals(
            result,
            [
                ('Mon', 0),
                ('Tue', 30047.0),
                ('Wed', 24465.0),
                ('Thu', 23705.0),
                ('Fri', 0),
                ('Sat', 0),
                ('Sun', 0),
                ],
            msg='Mean test error case 1'
            )
        weekdays_2 = utils.group_by_weekday(data[11])
        result_2 = [
            (calendar.day_abbr[weekday], utils.mean(intervals))
            for weekday, intervals in enumerate(weekdays_2)
        ]
        self.assertEquals(
            result_2,
            [
                ('Mon', 24123.0),
                ('Tue', 16564.0),
                ('Wed', 25321.0),
                ('Thu', 22984.0),
                ('Fri', 6426.0),
                ('Sat', 0),
                ('Sun', 0),
                ],
            msg='Mean test error',
            )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
