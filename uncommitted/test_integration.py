"""Test whether `uncommitted` works."""

import os
import shutil
import sys
import tempfile
import uncommitted.command
from subprocess import check_call
from textwrap import dedent

if sys.version_info.major > 2:
    from io import StringIO
else:
    from StringIO import StringIO

def create_checkouts(tempdir):
    cc = check_call
    cc(['git', 'config', '--global', 'user.email', 'you@example.com'])
    cc(['git', 'config', '--global', 'user.name', 'Your Name'])
    for system in 'git', 'hg', 'svn':
        for state in 'clean', 'dirty', 'ignoredirectory':
            d = os.path.join(tempdir, system + '-' + state)

            if system == 'svn':
                repo = d + '-repo'
                repo_url = 'file://' + repo.replace(os.sep, '/')
                cc(['svnadmin', 'create', repo])
                cc(['svn', 'co', repo_url, d])
            else:
                os.mkdir(d)
                cc([system, 'init', '.'], cwd=d)

            with open(os.path.join(d, 'maxim.txt'), 'w') as f:
                f.write(maxim)

            cc([system, 'add', 'maxim.txt'], cwd=d)
            cc([system, 'commit', '-m', 'Add a maxim'], cwd=d)

            if state == 'dirty' or state == 'ignoredirectory':
                with open(os.path.join(d, 'maxim.txt'), 'a') as f:
                    f.write(more_maxim)

def test_uncommitted():
    tempdir = tempfile.mkdtemp(prefix='uncommitted-test')
    try:
        create_checkouts(tempdir)
        sys.argv[:] = ['uncommitted', tempdir]
        io = StringIO()
        stdout = sys.stdout
        try:
            sys.stdout = io
            uncommitted.command.main()
        finally:
            sys.stdout = stdout
        result = io.getvalue()
    finally:
        shutil.rmtree(tempdir)
    assert result == expected.format(tempdir=tempdir)

def test_uncommittedIgnore():
    tempdir = tempfile.mkdtemp(prefix='uncommitted-test')
    try:
        create_checkouts(tempdir)
        """ Add ignore flag to skip ignore directories """
        sys.argv[:] = ['uncommitted', '-I', 'ignoredirectory', tempdir]
        io = StringIO()
        stdout = sys.stdout
        try:
            sys.stdout = io
            uncommitted.command.main()
        finally:
            sys.stdout = stdout
        result = io.getvalue()
    finally:
        shutil.rmtree(tempdir)
    assert result == expectedIgnore.format(tempdir=tempdir)

expected = dedent("""\
    {tempdir}/git-dirty - Git
     M maxim.txt

    {tempdir}/git-ignoredirectory - Git
     M maxim.txt

    {tempdir}/hg-dirty - Mercurial
     M maxim.txt

    {tempdir}/hg-ignoredirectory - Mercurial
     M maxim.txt

    {tempdir}/svn-dirty - Subversion
     M       maxim.txt

    {tempdir}/svn-ignoredirectory - Subversion
     M       maxim.txt

    """)

expectedIgnore = dedent("""\
    {tempdir}/git-dirty - Git
     M maxim.txt

    {tempdir}/hg-dirty - Mercurial
     M maxim.txt

    {tempdir}/svn-dirty - Subversion
     M       maxim.txt

    """)

maxim = dedent("""\
    A complex system that works
    is invariably found to have evolved
    from a simple system that worked.
    The inverse proposition also appears to be true:
    A complex system designed from scratch
    never works and cannot be made to work.
    """)

more_maxim = dedent("""\
    You have to start over,
    beginning with a working simple system.
    """)

if __name__ == '__main__':
    test_uncommitted()
    test_uncommittedIgnore()
