def yamlToReportRequests(config):
    structReport = []
    for report in config['reports']:
      structReportRequests = {'reportRequests':[], 'segmentsList': []}
      for metric in report.get('metrics'):
          structMetrics = []
          structDimensions = []
          structSegments = []
          segmentsList = []

          for expression in metric.get('expressions'):
            structMetrics.append({'expression': expression})

          if metric.get('dimensions'):
            for dimension in metric.get('dimensions'):
              structDimensions.append({'name': dimension})

          structReportRequest = {
            'viewId': report['viewId'],
            'dateRanges': [{'startDate': report['startDate'], 'endDate': report['endDate']}],
            'metrics': structMetrics,
            'dimensions': structDimensions
          }

          if metric.get('segments'):
            for segment in metric.get('segments'):
              segmentAlias = list(segment.keys())[0]
              segmentValue = list(segment.values())[0]
              structSegments.append({'segmentId': segmentValue})
              segmentsList.append({segmentValue: segmentAlias})

            structDimensions.append({'name': 'ga:segment'})
            structReportRequest['segments'] = structSegments

          structReportRequests['reportRequests'].append(structReportRequest)
          structReportRequests['segmentsList'].append(segmentsList)

      structReport.append(structReportRequests)

    return structReport
