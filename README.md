# Prometheus Google Analytics Reporting API (V4) Exporter

Exposes a set of basic metrics from the Google Analytics Reporting API (V4), to a Prometheus compatible endpoint. 
*This is a very basic implementation, designed for a specific purpose. If you wish to extend/fork this repo to be something greater...  We are more than open to any pull requests / feedback*

## Configuration

This exporter is setup to take the following parameters from environment variables:
* `BIND_PORT` The port you wish to run the container on, defaults to 9173
* `START_DATE` The start date you wish to pass to the API, you can't deal with totals here so set it to before you began monitoring. Format: `YYYY-MM-DD`
* `ACCOUNT_EMAIL` The email address of the service account given access to the API
* `VIEW_ID` The 'view_id' that google assigns to your sites statistics

Account email and view ID need to be obtained from your google account details. Details on how can be found [here](https://developers.google.com/analytics/devguides/reporting/core/v4/) You also need to supply a PEM file with a key to access the API, details on this link above.

## Install and deploy

Build a docker image:
```
docker build -t gar-exporter .
docker run \
  -p 9173:9173 \
  -e ACCOUNT_EMAIL="your@user.com" \
  gar-exporter
```

## Metrics

Metrics will be made available on port 9173 by default

## Unit Test
```
docker run \
  --name gar-exporter \
  --rm \
  -v $PWD:/usr/src/app \
  gar-exporter \
  python unitTest.py
```
