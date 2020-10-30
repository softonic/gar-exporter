def yamlToReportRequests(config):
    structReport = []
    for report in config['reports']:
      structReportRequests = {'reportRequests':[]}
      for metric in report.get('metrics'):
          structMetrics = []
          structDimensions = []

          for expression in metric.get('expressions'):
            structMetrics.append({'expression': expression})

          for dimension in metric.get('dimensions'):
            structDimensions.append({'name': dimension})

          structReportRequests['reportRequests'].append({
            'viewId': report['viewId'],
            'dateRanges': [{'startDate': report['startDate'], 'endDate': report['endDate']}],
            'metrics': structMetrics,
            'dimensions': structDimensions
          })
      structReport.append(structReportRequests)

    return structReport
