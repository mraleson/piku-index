import os
import json
from . import bundles


aliases = {}
missing = set([])
aliased = set([])

def loads():
    # path = os.path.join(os.path.dirname(__file__), '../data/packages.json.bak')
    # try:
    #     with open(path, 'r') as file:
    #         return json.load(file)
    # except FileNotFoundError:
    #     pass
    return {
        'index': {},
        'updated': None
    }

def save(index, file='packages.json'):
    path = os.path.join(os.path.dirname(__file__), f'../data/{file}')
    with open(path, 'w') as file:
        json.dump(index, file, indent=2)

def normalize_version(version):
    ver = version.lower()
    ver = version.lstrip('v')
    return ver

# find version of package released less than or equal to build date
def find_version(packages, package, build):
    original = package
    if package not in packages:
        if aliases.get(package) in packages:
            aliased.add(package)
            package = aliases.get(package)
    if package not in packages:
        missing.add(package)
        return None, None
    selected = None
    for version in packages[package]:
        candidate = packages[package][version]['bundle']['build']
        if candidate <= build:
            selected = version
    return package, selected

def update():
    bundle_names = ['community', 'adafruit']
    circuit_python_versions = ['6', '7']

    # get index
    index = loads()

    # build index
    for target in circuit_python_versions:
        # ensure target exists in index
        if target not in index['index']:
            index['index'][target] = {}

        for bundle in bundle_names:
            # get builds
            builds = bundles.get_builds(bundle, target)

            for build in builds:
                # get index and zip urls
                index_url = builds[build]['index']
                build_url = builds[build]['build']
                print(target, bundle, build)

                # update index for each package in bundle manifest
                packages = bundles.get_index(index_url)
                for package in packages:
                    # decompose package info
                    package_info = packages[package]
                    version = normalize_version(package_info['version'])

                    # ensure package structure
                    if package not in index['index'][target]:
                        index['index'][target][package] = {}

                    # update package index
                    # (don't overwrite older releases of the same version it breaks dependency resolution)
                    if version not in index['index'][target][package]:
                        index['index'][target][package][version] = {
                            'package': package,
                            'version': package_info['version'],
                            'bundle': {
                                'name': bundle,
                                'build': build,
                                'target': target,
                                'url': build_url,},
                            'path': package_info['path'],
                            'hash': None,
                            'dependencies': None,
                            'raw': package_info}

    # before dependency resolution
    save(index, 'packages.json.bak')

    # find package aliases
    for target in index['index']:
        for package in index['index'][target]:
            for version in index['index'][target][package]:
                name = index['index'][target][package][version]['package']
                pypi = index['index'][target][package][version]['raw'].get('pypi_name')
                if pypi:
                    aliases[pypi] = name
                    if 'busdevice' in pypi:
                        aliases[pypi.replace('busdevice', 'bus-device')] = name
                    aliases[pypi.replace('adafruit-circuitpython-', 'adafruit_circuitpython_')] = name
                    aliases[pypi.replace('-', '_').replace('adafruit_circuitpython_', 'adafruit-circuitpython-')] = name

    # resolve dependencies
    for target in index['index']:
        for package in index['index'][target]:
            for version in index['index'][target][package]:
                # find dependency version with closest release to build date
                package_info = index['index'][target][package][version]
                raw_info = package_info['raw']
                package_build = package_info['bundle']['build']
                dependencies = {}
                for dependency in raw_info['dependencies'] + raw_info.get('external_dependencies', []):
                    dep, ver = find_version(index['index'][target], dependency, package_build)
                    if ver:
                        dependencies[dep] = ver
                index['index'][target][package][version]['dependencies'] = dependencies

    # show unresolved dependencies
    print('***unresolved dependencies')
    for m in missing:
        print(m)

    # show aliased dependencies
    print('***aliased dependencies')
    for m in aliased:
        print(m)

    # save index
    save(index)

def upload():
    pass
