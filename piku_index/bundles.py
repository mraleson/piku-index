import re
import requests
from xml.etree import ElementTree


bucket='adafruit-circuit-python'

# get collection of all builds for bundle
def get_builds(bundle, target):
    last = None
    bundles = {}
    bucket_url = f'https://{bucket}.s3.amazonaws.com'
    bundle_index_pattern = re.compile(r'.+bundle\-(\d+)\.json')
    bundle_build_pattern = re.compile(r'.+mpy\-(\d+)\.zip')

    # create build index
    finished = False
    while not finished:
        response = requests.get(bucket_url, params={
            'list-type': '2',
            'delimiter': '/',
            'prefix': f'bundles/{bundle}/',
            'max-keys': 100,
            'start-after': last
        })
        root = ElementTree.fromstring(response.content)
        finished = root.find('{*}IsTruncated').text != 'true'
        files = [e.find('{*}Key').text for e in root.findall('{*}Contents')]
        if files:
            last = files[-1]
        for file in files:
            if bundle_index_pattern.match(file):
                build_target = bundle_index_pattern.findall(file)[0]
                if build_target not in bundles:
                    bundles[build_target] = {'index': None, 'builds': []}
                bundles[build_target]['index'] = file
            elif bundle_build_pattern.match(file):
                build_target = bundle_build_pattern.findall(file)[0]
                if build_target not in bundles:
                    bundles[build_target] = {'index': None, 'builds': []}
                bundles[build_target]['builds'].append(file)

    # reduce to bundles with a build matching target
    pruned = {}
    for key, value in bundles.items():
        builds = [b for b in value['builds'] if f'{target}.x' in b]
        if builds:
            pruned[key] = {
                'index': f'https://{bucket}.s3.amazonaws.com/{value["index"]}',
                'build': f'https://{bucket}.s3.amazonaws.com/{builds[-1]}',
            }
    return pruned

# get package index given valid bundle and build tag
def get_index(url):
    response = requests.get(url)
    package_index = response.json()
    if not package_index or response.status_code != 200:
        return None
    return package_index
