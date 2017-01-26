import argparse
import importlib # available from PyPI for Python <2.7

version_location = '_version' # in python relative module notation

parser = argparse.ArgumentParser(
    description='Release a new version of PyHEADTAIL in 2 steps.')
parser.add_argument(
    'part', type=str,
    choices=['major', 'minor', 'patch'],
    help="release type (use 'minor' for new features and 'patch' for bugfixes, "
         "'major' is not usually used ;-)",
)

def bumpversion(version, part):
    '''Advance the three component version with format X.Y.Z by one in the
    given part. Return the bumped version string.
    Arguments:
        - version: string, format 'major.minor.patch' (e.g. '1.12.2')
        - part: string, one of ['major', 'minor', 'patch']
    '''
    parts = {}
    # exactly 3 components in version:
    parts['major'], parts['minor'], parts['patch'] = version.split('.')
    # only integers stored:
    assert all(parts[p].isdigit() for p in parts)
    try:
        subversion = int(parts[part])
        subversion += 1
        parts[part] = str(subversion)
    except KeyError:
        raise ValueError('The given part "' + part + '" is not in '
                         "['major', 'minor', 'patch'].")
    bumpedversion = '{0}.{1}.{2}'.format(
        parts['major'], parts['minor'], parts['patch'])
    return bumpedversion


if __name__ == '__main__':
    args = parser.parse_args()
    version = importlib.import_module(version_location).__version__
    print (bumpversion(version, args.part))
