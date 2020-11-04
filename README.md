# Prometheus Google Analytics Reporting API (V4) Exporter

Exposes a set of basic metrics from the Google Analytics Reporting API (V4), to a Prometheus compatible endpoint. 
*This is a very basic implementation, designed for a specific purpose. If you wish to extend/fork this repo to be something greater...  We are more than open to any pull requests / feedback*

## Configuration

This exporter is set up to take the following parameters from environment variables:
* `BIND_PORT` The port you wish to run the container on, defaults to 9173

The view ID need to be obtained from your Google account details. Details on how can be found [here](https://developers.google.com/analytics/devguides/reporting/core/v4/)
You also need to supply a JSON service account file, details on this link above.

On other hand the reports need to be defined in a YAML file with a structure like this:

```yaml
reports:
  - viewId: '<VIEW-ID-1>'
    startDate: 'today'
    endDate: 'today'
    metrics:
      - expressions:
          - 'ga:totalEvents'
          - 'ga:uniqueEvents'
        dimensions:
          - 'ga:dimension1'
      - expressions:
          - 'ga:avgServerResponseTime'
          - 'ga:avgPageLoadTime'
        dimensions:
          - 'ga:eventAction'
  - viewId: '<VIEW-ID-2>'
    startDate: '2020-01-01'
    endDate: 'today'
    metrics:
      - expressions:
          - 'ga:totalEvents'
          - 'ga:uniqueEvents'
        dimensions:
          - 'ga:eventAction'
  - viewId: '<VIEW-ID-2>'
    startDate: '2020-11-01'
    endDate: 'today'
    metrics:
      - expressions:
          - 'ga:sessions'
        dimensions:
          - 'ga:deviceCategory'
        segments:
          - regionA: 'sessions::condition::ga:country=~United States|united kingdom|canada|australia|new zealand|ireland'
```
You can add as many VIEW-IDs as you want and define the metrics to obtain in blocks of 10 requests as much, it's a limitation of the GA API.
Another limitation is that the segments definition need to be shared in the request block, it supports to define an alias as key in the segment definition
to identify it correctly in the prometheus output.

Output sample in metrics port:
```
curl -s localhost:9173
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 1187.0
...
# HELP ga_reporting_sessions sessions
# TYPE ga_reporting_sessions gauge
ga_reporting_sessions{dateEnd="today",dateStart="2020-11-01",deviceCategory="desktop",viewId="123456789"} 3.669896e+06
# HELP ga_reporting_sessions sessions
# TYPE ga_reporting_sessions gauge
ga_reporting_sessions{dateEnd="today",dateStart="2020-11-01",deviceCategory="mobile",viewId="123456789"} 3.554143e+06
# HELP ga_reporting_sessions sessions
# TYPE ga_reporting_sessions gauge
ga_reporting_sessions{dateEnd="today",dateStart="2020-11-01",deviceCategory="tablet",viewId="123456789"} 179754.0
# HELP ga_reporting_sessions sessions
# TYPE ga_reporting_sessions gauge
ga_reporting_sessions{dateEnd="today",dateStart="2020-11-01",deviceCategory="desktop",segment="regionA",viewId="123456789"} 328426.0
# HELP ga_reporting_sessions sessions
# TYPE ga_reporting_sessions gauge
ga_reporting_sessions{dateEnd="today",dateStart="2020-11-01",deviceCategory="mobile",segment="regionA",viewId="123456789"} 111453.0
# HELP ga_reporting_sessions sessions
# TYPE ga_reporting_sessions gauge
ga_reporting_sessions{dateEnd="today",dateStart="2020-11-01",deviceCategory="tablet",segment="regionA",viewId="123456789"} 20842.0
# HELP ga_reporting_totalEvents totalEvents
# TYPE ga_reporting_totalEvents gauge
ga_reporting_totalEvents{dateEnd="today",dateStart="today",eventAction="100%",viewId="987654321"} 29.0
...
```

The application expects to find the config file in the path `/usr/src/app/config.yaml`, and the credentials file need to 

## Install and deploy

Build a docker image:
```
docker build -t gar-exporter . &&\
docker run \
  -p 9173:9173 \
  -e CONFIG_FILE=/etc/gar-exporter/config.yaml \
  -e SERVICE_ACCOUNT_FILE=/etc/gar-exporter/ga_creds.json \
  -v $PWD/ga_creds.json:/etc/gar-exporter/ga_creds.json \
  -v $PWD/config.yaml:/etc/gar-exporter/config.yaml \
  gar-exporter
```

You have a build image available in https://hub.docker.com/repository/docker/softonic/gar-exporter
Instead of build your own image you can use it with:
```
docker pull softonic/gar-exporter:latest &&\
docker run \
  -p 9173:9173 \
  -e CONFIG_FILE=/etc/gar-exporter/config.yaml \
  -e SERVICE_ACCOUNT_FILE=/etc/gar-exporter/ga_creds.json \
  -v $PWD/ga_creds.json:/etc/gar-exporter/ga_creds.json \
  -v $PWD/config.yaml:/etc/gar-exporter/config.yaml \
  -v $PWD/gar_exporter.py:/usr/src/app/gar_exporter.py \
  softonic/gar-exporter:latest
```

### Deploy via Helm chart to Kubernetes
This is provided with a Helm chart that can be used to install this system in a Kubernetes cluster.
You need to provide a secret with the service account data and reference it in the `values.yaml` file.

```
helm upgrade --install --namespace gar-exporter gar-exporter helm/gar-exporter
```

## Metrics
If you don't provide the `BIND_PORT` parameter metrics will be made available on port 9173 by default

## Unit Test
There's a basic Unit Test created that you can launch to check the reports YAML configuration structure fits what the Google API expects to get.

```
docker run \
  --name gar-exporter \
  --rm \
  -v $PWD:/usr/src/app \
  gar-exporter \
  python unitTest.py
```
