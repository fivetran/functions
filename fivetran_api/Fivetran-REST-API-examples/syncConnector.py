import json
import requests
import argparse

class Connector:
  def __init__(self, apiKey, apiSecret, version=None):
    self._api_version = self._set_api_version(version)
    self._api_endpoint = 'https://api.fivetran.com/{version}/connectors'.format(
      version=self._api_version
    )

    self._auth = requests.auth.HTTPBasicAuth(apiKey, apiSecret)

  def _set_api_version(self, version):
    if version is None:
      version = 'v1'
    return version

  def getApiEndpoint(self):
    return self._api_endpoint

  def sync(self, connectorId):
    sync_endpoint = '{endpoint}/{connectorId}/force'.format(
      endpoint=self.getApiEndpoint(),
      connectorId=connectorId
    )
    
    r = requests.post(
      sync_endpoint,
      auth=self._auth
      # json=payload
    ).json()

    print('Result:', r['code'], r['message'])

    return r


def main():
  parser = argparse.ArgumentParser(description="Sync a connector")
  parser.add_argument("--api_key")
  parser.add_argument("--api_secret")
  parser.add_argument("--connector_id")

  args = parser.parse_args()

  apiKey = args.api_key
  apiSecret = args.api_secret
  connectorId = args.connector_id

  c = Connector(
    apiKey=apiKey,
    apiSecret=apiSecret
  )

  c.sync(
    connectorId
  )

if __name__ == '__main__':
  main()

  


