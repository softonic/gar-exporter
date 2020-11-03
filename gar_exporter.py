from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import time, httplib2, os, bios, helper

class GarCollector(object):
  def collect(self):
    self._gauges = {}
    analytics = self._initialize_analyticsreporting()
    print("Authorized to talk with Analytics v4 API")
    reports = helper.yamlToReportRequests(bios.read(CONFIG_FILE))
    for report in reports:
        print("[REPORT REQUEST] ", report)
        segmentsList = report['segmentsList']
        del report['segmentsList']

        response = self._get_report(analytics, report)
        print("[RESPONSE OBTAINED]")
        self._get_metrics(
          response,
          report.get('reportRequests')[0].get('viewId'),
          report.get('reportRequests')[0].get('dateRanges')[0],
          segmentsList
        )

        for metric in self._gauges:
          yield self._gauges[metric]

  def _initialize_analyticsreporting(self):

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
      SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    http = credentials.authorize(httplib2.Http())
    analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

    return analytics

  def _get_report(self, analytics, report):

    return analytics.reports().batchGet(
      body=report
    ).execute()

  def _get_metrics(self, response, viewId, dateRanges, segmentsList):
    METRIC_PREFIX = 'ga_reporting'
    LABELS = ['ga:viewId', 'ga:dateStart', 'ga:dateEnd']
    self._gauges = {}

    for report in response.get('reports', []):
      columnHeader = report.get('columnHeader', {})
      dimensionHeaders = LABELS
      dimensionHeaders.extend(columnHeader.get('dimensions', []))

      # Added dimensions as labels - fixed bug
      dimensionHeadersModified = [x[3:] for x in dimensionHeaders]

      metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
      rows = report.get('data', {}).get('rows', [])

      testi=0
      for row in rows:
        dimensions = [viewId, dateRanges.get('startDate'), dateRanges.get('endDate')]
        dimensions.extend(row.get('dimensions', []))

        dateRangeValues = row.get('metrics', [])

        for i, element in enumerate(dimensions):
          if element == 'Dynamic Segment':
            dimensions[i] = list(segmentsList[0][0].values())[0]

        testi+=1
        dimension=""
#         for header, dimension in zip(dimensionHeaders, dimensions):
#           print("[HEADER] " + header + ': ' + dimension)

        for i, values in enumerate(dateRangeValues):
#           print('Date range (' + str(i) + ')')

          for metricHeader, returnValue in zip(metricHeaders, values.get('values')):
            metric = metricHeader.get('name')[3:]
#             print("[METRIC] " + metric + ': ' + returnValue)
            self._gauges[metric+str(testi)] = GaugeMetricFamily('%s_%s' % (METRIC_PREFIX, metric), '%s' % metric, value=None, labels=dimensionHeadersModified)
            self._gauges[metric+str(testi)].add_metric(dimensions, value=float(returnValue))

if __name__ == '__main__':
  SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
  DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
  SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
  CONFIG_FILE=os.getenv('CONFIG_FILE')

  print("Starting server in 0.0.0.0:" + os.getenv('BIND_PORT'))
  start_http_server(int(os.getenv('BIND_PORT')))
  REGISTRY.register(GarCollector())
  print("Waiting for serving metrics")
  while True: time.sleep(1)
