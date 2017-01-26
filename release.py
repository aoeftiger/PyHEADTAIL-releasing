'''
Algorithm to release PyHEADTAIL versions. The structure follows the development
workflow, cf. the PyHEADTAIL wiki:
https://github.com/PyCOMPLETE/PyHEADTAIL/wiki/Our-Development-Workflow

Requires git, hub (the github tool, https://hub.github.com/) and importlib
(included in python >=2.7) installed.

@copyright: CERN
@date: 26.01.2017
@author: Adrian Oeftiger
'''

import argparse
import importlib # available from PyPI for Python <2.7
import os, subprocess

# CONFIG
version_location = '_version' # in python relative module notation
test_script_location = 'pre-push' # in python relative module notation
release_branch_prefix = 'release/v' # prepended name of release branch


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

def current_branch():
    '''Return current git branch name.'''
    # get the current branch name, strip trailing whitespaces using rstrip()
    return subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"]).rstrip().decode("utf-8")

def open_release_branch(version):
    '''Create release/vX.Y.Z branch with the given version string.
    Push the new release branch upstream. Print output from git.
    '''
    branch_name = release_branch_prefix + version
    output = subprocess.check_output(
        ["git", "checkout", "-b", branch_name]
    ).rstrip().decode("utf-8")
    print (output)
    output = subprocess.check_output(
        ["git", "push", "--set-upstream", "origin", branch_name]
    ).rstrip().decode("utf-8")
    print (output)

def ensure_tests(test_script_location):
    '''Run test script and return whether they were successful.'''
    test_script = importlib.import_module(test_script_location)
    return test_script.run()

def is_worktree_dirty():
    '''Return True if the current git work tree is dirty, i.e.\ the
    status whether or not there are uncommitted changes.
    '''
    # integer (0: clean, 1: dirty)
    is_dirty = subprocess.call(['git', 'diff', '--quiet', 'HEAD', '--'])
    return bool(is_dirty)

def git_status():
    '''Print git status output.'''
    output = subprocess.check_output(
        ['git', 'status', 'HEAD']
    )
    print (output)


# DEFINE TWO STEPS FOR RELEASE PROCESS:

def init_release(version, part):
    '''Initialise release process.'''
    if not current_branch() == 'develop':
        raise EnvironmentError(
            'Releases can only be initiated from the develop branch!')
    if is_worktree_dirty():
        git_status()
        raise EnvironmentError('Release process can only be initiated on '
                               'a clean git repository. You have uncommitted '
                               'changes in your files, please fix this first.')
    version = bumpversion(version, part)
    open_release_branch(version)
    print ('*** The release process has been successfully initiated.\n'
           'Opening the pull request into master from the just created '
           'release branch.\n\n'
           'You may have to provide your github.com credentials '
           'to the following hub call. Then describe the new release in '
           'the opened editor.')
    subprocess.call(["hub", "pull-request"])
    print ('*** Please check that the PyHEADTAIL tests run successfully.')

def finalise_release(version):
    '''Finalise release process.'''
    tests_successful = ensure_tests(test_script_location)
    if not tests_successful:
        raise EnvironmentError('The PyHEADTAIL tests fail. Please fix '
                               'the tests first!')
    print ('*** The PyHEADTAIL tests have successfully terminated.')




# ALGORITHM FOR RELEASE PROCESS:
if __name__ == '__main__':
    args = parser.parse_args()
    version = importlib.import_module(version_location).__version__

    print ('Current working directory:\n' + os.getcwd() + '\n')

    # are we on a release branch already?
    if not (current_branch()[:len(release_branch_prefix)] ==
            release_branch_prefix):
        init_release(version, args.part)
    else:
        finalise_release(version)
