# Prometheus Google Analytics Reporting API (V4) Exporter

Exposes a set of basic metrics from the Google Analytics Reporting API (V4), to a Prometheus compatible endpoint. 
*This is a very basic implementation, designed for a specific purpose. If you wish to extend/fork this repo to be something greater...  We are more than open to any pull requests / feedback*

## Configuration

This exporter is set up to take the following parameters from environment variables:
* `BIND_PORT` The port you wish to run the container on, defaults to 9173
* `ACCOUNT_EMAIL` The email address of the service account given access to the API

Account email and view ID need to be obtained from your Google account details. Details on how can be found [here](https://developers.google.com/analytics/devguides/reporting/core/v4/)
You also need to supply a PEM file (P12 format) with a key to access the API, details on this link above.

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
```
You can add as many VIEW-IDs as you want and define the metrics to obtain in blocks of 10 requests as much, it's a limitation of the GA API.

The application expects to find the config file in the path `/usr/src/app/config.yaml`, and the credentials file in `/usr/src/app/client_secrets.p12`.

## Install and deploy

Build a docker image:
```
docker build -t gar-exporter . &&\
docker run \
  -p 9173:9173 \
  -e ACCOUNT_EMAIL="your@user.com" \
  -v $PWD/client_secrets.p12:/usr/src/app/client_secrets.p12 \
  -v $PWD/config.yaml:/usr/src/app/config.yaml \
  gar-exporter
```

You have a build image available in https://hub.docker.com/repository/docker/softonic/gar-exporter
Instead of build your own image you can use it with:
```
docker pull softonic/gar-exporter:latest &&\
docker run \
  -p 9173:9173 \
  -e ACCOUNT_EMAIL="your@user.com" \
  -v $PWD/client_secrets.p12:/usr/src/app/client_secrets.p12 \
  -v $PWD/config.yaml:/usr/src/app/config.yaml \
  softonic/gar-exporter:latest
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
