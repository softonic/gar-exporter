import unittest

import helper, yaml

class TestGarExporter(unittest.TestCase):
    def test_yaml_to_reportRequests(self):
        inputyaml ="""reports:
  - viewId: 176788503
    startDate: '2020-10-27'
    endDate: today
    metrics:
      - expressions:
          - ga:totalEvents
          - ga:uniqueEvents
        dimensions:
          - ga:eventAction
      - expressions:
          - ga:pageviews
          - ga:avgPageLoadTime
          - ga:uniqueEvents
        dimensions:
          - ga:country
          - ga:networkLocation
  - viewId: 123312344
    startDate: '2020-01-01'
    endDate: '2020-09-01'
    metrics:
      - expressions:
          - ga:sessions
          - ga:pageviews
          - ga:users
        dimensions:
          - ga:eventCategory
"""
        expectedOutput = [
          {
          'reportRequests':
            [
              {
                 'viewId': 176788503,
                 'dateRanges': [{'startDate': '2020-10-27', 'endDate': 'today'}],
                 'metrics': [{'expression': 'ga:totalEvents'}, {'expression': 'ga:uniqueEvents'}],
                 'dimensions': [{'name': 'ga:eventAction'}]
              },
              {
                 'viewId': 176788503,
                 'dateRanges': [{'startDate': '2020-10-27', 'endDate': 'today'}],
                 'metrics': [{'expression': 'ga:pageviews'}, {'expression': 'ga:avgPageLoadTime'}, {'expression': 'ga:uniqueEvents'}],
                 'dimensions': [{'name': 'ga:country'}, {'name': 'ga:networkLocation'}]
              },
            ]
          },
          {
            'reportRequests':
              [
                {
                   'viewId': 123312344,
                   'dateRanges': [{'startDate': '2020-01-01', 'endDate': '2020-09-01'}],
                   'metrics': [{'expression': 'ga:sessions'}, {'expression': 'ga:pageviews'}, {'expression': 'ga:users'}],
                   'dimensions': [{'name': 'ga:eventCategory'}]
                },
              ]
            }
        ]
        output = helper.yamlToReportRequests(yaml.load(inputyaml,Loader=yaml.FullLoader))
#         print("......................")
#         print("OUTPUT!")
#         print(output)
#         print("......................")
#         print("EXPECTED OUTPUT!")
#         print(expectedOutput)
#         print("......................")
        self.assertEqual(
            output
            , expectedOutput
        )

if __name__ == '__main__':
    unittest.main()
