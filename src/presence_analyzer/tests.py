# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
# pylint: disable=maybe-no-member, too-many-public-methods, missing-docstring,
# pylint: disable=unused-import
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


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

    def test_presence_start_end_view(self):
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
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
            datetime.time(9, 39, 5)
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
