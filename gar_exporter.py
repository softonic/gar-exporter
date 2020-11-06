from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from apiclient.discovery import build
from apiclient.errors import HttpError
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

import time, httplib2, os, bios, helper, json

class GarCollector(object):
  lastResponses = {}

  def collect(self):
    self._gauges = {}
    analytics = self._initialize_analyticsreporting()
    print("[",datetime.now(),"]","Authorized to talk with Analytics v4 API")
    reports = helper.yamlToReportRequests(bios.read(CONFIG_FILE))
    for report in reports:
        print("[",datetime.now(),"]","[REPORT REQUEST]", report)
        segmentsList = report['segmentsList']
        del report['segmentsList']

        response = self._requestWithExponentialBackoff(analytics, report)
        print("[",datetime.now(),"]","RESPONSE OBTAINED")
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

  def _requestWithExponentialBackoff(self, analytics, report):
      """Wrapper to request Google Analytics data with exponential backoff.

      The makeRequest method accepts the analytics service object, makes API
      requests and returns the response. If any error occurs, the makeRequest
      method is retried using exponential backoff.

      Args:
        analytics: The analytics service object
        report: Report request structure

      Returns:
        The API response from the _get_report method.
      """

      reportId = hash(json.dumps(report))
      for n in range(0, 5):
        try:
          response = self._get_report(analytics, report)
          self.lastResponses[reportId] = response
          return response

        except HttpError as error:
          if error.resp.reason in ['userRateLimitExceeded', 'quotaExceeded',
                                   'internalServerError', 'backendError']:
            time.sleep((2 ** n) + random.random())
            print("[WARNING] Http request error", error.resp.reason)
          else:
            break

      print("[",datetime.now(),"]","[ERROR] There has been an error, the request never succeeded, returning earlier result")
      return self.lastResponses[reportId]

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

  print("[",datetime.now(),"]","Starting server in 0.0.0.0:" + os.getenv('BIND_PORT'))
  start_http_server(int(os.getenv('BIND_PORT')))
  REGISTRY.register(GarCollector())
  print("[",datetime.now(),"]","Waiting for serving metrics")
  while True: time.sleep(1)
