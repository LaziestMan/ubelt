from os.path import isdir
from os.path import isfile
from os.path import join, exists, islink
import ubelt as ub
import pytest
import os
from ubelt import util_platform


def test_delete_symlinks():
    """
    CommandLine:
        python -m ubelt.tests.test_links test_delete_symlinks
    """
    # TODO: test that we handle broken links
    dpath = ub.ensure_app_resource_dir('ubelt', 'test_delete_links')

    happy_dpath = join(dpath, 'happy_dpath')
    happy_dlink = join(dpath, 'happy_dlink')
    happy_fpath = join(dpath, 'happy_fpath.txt')
    happy_flink = join(dpath, 'happy_flink.txt')
    broken_dpath = join(dpath, 'broken_dpath')
    broken_dlink = join(dpath, 'broken_dlink')
    broken_fpath = join(dpath, 'broken_fpath.txt')
    broken_flink = join(dpath, 'broken_flink.txt')

    def check_path_condition(path, positive, want, msg):
        if not want:
            positive = not positive
            msg = 'not ' + msg

        if not positive:
            dirstats(dpath)
            print('About to raise error: {}'.format(msg))
            print('path = {!r}'.format(path))
            print('exists(path) = {!r}'.format(exists(path)))
            print('islink(path) = {!r}'.format(islink(path)))
            print('isdir(path) = {!r}'.format(isdir(path)))
            print('isfile(path) = {!r}'.format(isfile(path)))
            raise AssertionError('path={} {}'.format(path, msg))

    def assert_sometrace(path, want=True):
        # Either exists or is a broken link
        positive = exists(path) or islink(path)
        check_path_condition(path, positive, want, 'has trace')

    def assert_broken_link(path, want=True):
        if util_platform._can_symlink():
            print('path={} should{} be a broken link'.format(
                path, ' ' if want else ' not'))
            positive = not exists(path) and islink(path)
            check_path_condition(path, positive, want, 'broken link')
        else:
            # TODO: we can test this
            # positive = util_platform._win32_is_junction(path)
            print('path={} should{} be a broken link (junction)'.format(
                path, ' ' if want else ' not'))
            print('cannot check this yet')
            # We wont be able to differentiate links and nonlinks for junctions
            # positive = exists(path)
            # check_path_condition(path, positive, want, 'broken link')

    dirstats(dpath)
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)
    dirstats(dpath)

    ub.ensuredir(happy_dpath, verbose=2)
    ub.ensuredir(broken_dpath, verbose=2)
    ub.touch(happy_fpath, verbose=2)
    ub.touch(broken_fpath, verbose=2)
    dirstats(dpath)

    ub.symlink(broken_fpath, broken_flink, verbose=2)
    ub.symlink(broken_dpath, broken_dlink, verbose=2)
    ub.symlink(happy_fpath, happy_flink, verbose=2)
    ub.symlink(happy_dpath, happy_dlink, verbose=2)
    dirstats(dpath)

    # Deleting the files should not delete the symlinks (windows)
    ub.delete(broken_fpath, verbose=2)
    dirstats(dpath)

    ub.delete(broken_dpath, verbose=2)
    dirstats(dpath)

    assert_broken_link(broken_flink, 1)
    assert_broken_link(broken_dlink, 1)
    assert_sometrace(broken_fpath, 0)
    assert_sometrace(broken_dpath, 0)

    assert_broken_link(happy_flink, 0)
    assert_broken_link(happy_dlink, 0)
    assert_sometrace(happy_fpath, 1)
    assert_sometrace(happy_dpath, 1)

    # broken symlinks no longer exist after they are deleted
    ub.delete(broken_dlink, verbose=2)
    dirstats(dpath)
    assert_sometrace(broken_dlink, 0)

    ub.delete(broken_flink, verbose=2)
    dirstats(dpath)
    assert_sometrace(broken_flink, 0)

    # real symlinks no longer exist after they are deleted
    # but the original data is fine
    ub.delete(happy_dlink, verbose=2)
    dirstats(dpath)
    assert_sometrace(happy_dlink, 0)
    assert_sometrace(happy_dpath, 1)

    ub.delete(happy_flink, verbose=2)
    dirstats(dpath)
    assert_sometrace(happy_flink, 0)
    assert_sometrace(happy_fpath, 1)


def test_modify_directory_symlinks():
    dpath = ub.ensure_app_resource_dir('ubelt', 'test_modify_symlinks')
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)

    happy_dpath = join(dpath, 'happy_dpath')
    happy_dlink = join(dpath, 'happy_dlink')
    ub.ensuredir(happy_dpath, verbose=2)

    ub.symlink(happy_dpath, happy_dlink, verbose=2)

    # Test file inside directory symlink
    file_path1 = join(happy_dpath, 'file.txt')
    file_path2 = join(happy_dlink, 'file.txt')

    ub.touch(file_path1, verbose=2)
    assert exists(file_path1)
    assert exists(file_path2)

    ub.writeto(file_path1, 'foo')
    assert ub.readfrom(file_path1) == 'foo'
    assert ub.readfrom(file_path2) == 'foo'

    ub.writeto(file_path2, 'bar')
    assert ub.readfrom(file_path1) == 'bar'
    assert ub.readfrom(file_path2) == 'bar'

    ub.delete(file_path2, verbose=2)
    assert not exists(file_path1)
    assert not exists(file_path2)

    # Test directory inside directory symlink
    dir_path1 = join(happy_dpath, 'dir')
    dir_path2 = join(happy_dlink, 'dir')

    ub.ensuredir(dir_path1, verbose=2)
    assert exists(dir_path1)
    assert exists(dir_path2)

    subfile_path1 = join(dir_path1, 'subfile.txt')
    subfile_path2 = join(dir_path2, 'subfile.txt')

    ub.writeto(subfile_path2, 'foo')
    assert ub.readfrom(subfile_path1) == 'foo'
    assert ub.readfrom(subfile_path2) == 'foo'

    ub.writeto(subfile_path1, 'bar')
    assert ub.readfrom(subfile_path1) == 'bar'
    assert ub.readfrom(subfile_path2) == 'bar'

    ub.delete(dir_path1, verbose=2)
    assert not exists(dir_path1)
    assert not exists(dir_path2)


def test_modify_file_symlinks():
    """
    CommandLine:
        python -m ubelt.tests.test_links test_modify_symlinks
    """
    # TODO: test that we handle broken links
    dpath = ub.ensure_app_resource_dir('ubelt', 'test_modify_symlinks')
    happy_fpath = join(dpath, 'happy_fpath.txt')
    happy_flink = join(dpath, 'happy_flink.txt')
    ub.touch(happy_fpath, verbose=2)

    ub.symlink(happy_fpath, happy_flink, verbose=2)

    # Test file symlink
    ub.writeto(happy_fpath, 'foo')
    assert ub.readfrom(happy_fpath) == 'foo'
    assert ub.readfrom(happy_flink) == 'foo'

    ub.writeto(happy_flink, 'bar')
    assert ub.readfrom(happy_fpath) == 'bar'
    assert ub.readfrom(happy_flink) == 'bar'


def dirstats(dpath=None):
    """
    CommandLine:
        python -m ubelt.tests.test_links dirstats
    """
    if dpath is None:
        dpath = os.getcwd()
    print('===============')
    print('Listing for dpath={}'.format(dpath))
    print('E L F D J - path')
    print('--------------')
    if not os.path.exists(dpath):
        print('... does not exist')
        return
    entries = []
    for path in sorted(os.listdir(dpath)):
        full_path = join(dpath, path)
        E = os.path.exists(full_path)
        L = os.path.islink(full_path)
        F = os.path.isfile(full_path)
        D = os.path.isdir(full_path)
        J = util_platform._win32_is_junction(full_path)
        ELFD = [E, L, F, D]
        ELFDJ = [E, L, F, D, J]
        if ELFD == [1, 0, 0, 1]:
            path = ub.color_text(path, 'blue')
        elif ELFD == [1, 0, 1, 0]:
            path = ub.color_text(path, 'white')
        elif ELFD == [1, 1, 0, 1]:
            path = ub.color_text(path, 'green')
        elif ELFD == [1, 1, 1, 0]:
            path = ub.color_text(path, 'yellow')
        elif ELFD == [0, 1, 0, 0]:
            path = ub.color_text(path, 'red')
        elif ELFD == [0, 1, 0, 1]:
            pass
        elif ELFD == [0, 0, 0, 1]:
            pass
        elif ELFD == [0, 0, 1, 0]:
            pass
            # path = ub.color_text(path, 'red')
        elif ELFD == [0, 0, 0, 0]:
            print('path = {!r}'.format(path))
            print('dpath = {!r}'.format(dpath))
            print('\n'.join(sorted(entries)))
            raise ValueError(dpath)
        else:
            print('path = {!r}'.format(path))
            print('dpath = {!r}'.format(dpath))
            print('\n'.join(sorted(entries)))
            raise AssertionError(str(ELFDJ) + str(path))
        line = '{E:d} {L:d} {F:d} {D:d} {J:d} - {path}'.format(**locals())
        if os.path.islink(full_path):
            line += ' -> ' + os.readlink(full_path)
        entries.append(line)
    print('\n'.join(sorted(entries)))


def test_broken_link():
    """
    CommandLine:
        python -m ubelt.tests.test_links test_broken_link
    """
    dpath = ub.ensure_app_resource_dir('ubelt', 'test_broken_link')

    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)
    dirstats(dpath)

    broken_fpath = join(dpath, 'broken_fpath.txt')
    broken_flink = join(dpath, 'broken_flink.txt')

    ub.touch(broken_fpath, verbose=2)
    dirstats(dpath)
    ub.symlink(broken_fpath, broken_flink, verbose=2)

    dirstats(dpath)
    ub.delete(broken_fpath, verbose=2)

    dirstats(dpath)

    # make sure I am sane that this is the correct check.
    can_symlink = util_platform._can_symlink()
    print('can_symlink = {!r}'.format(can_symlink))
    if can_symlink:
        # normal behavior
        assert os.path.islink(broken_flink)
        assert not os.path.exists(broken_flink)
    else:
        # on windows hard links are essentially the same file.
        # there is no trace that it was actually a link.
        assert os.path.exists(broken_flink)


def test_overwrite_symlink():
    """
    CommandLine:
        python -m ubelt.tests.test_links test_overwrite_symlink
    """

    # TODO: test that we handle broken links
    dpath = ub.ensure_app_resource_dir('ubelt', 'test_overwrite_symlink')
    ub.delete(dpath, verbose=2)
    ub.ensuredir(dpath, verbose=2)

    happy_fpath = join(dpath, 'happy_fpath.txt')
    other_fpath = join(dpath, 'other_fpath.txt')
    happy_flink = join(dpath, 'happy_flink.txt')

    for verbose in [2, 1, 0]:
        print('=======')
        print('verbose = {!r}'.format(verbose))
        ub.delete(dpath, verbose=verbose)
        ub.ensuredir(dpath, verbose=verbose)
        ub.touch(happy_fpath, verbose=verbose)
        ub.touch(other_fpath, verbose=verbose)

        dirstats(dpath)
        ub.symlink(happy_fpath, happy_flink, verbose=verbose)

        # Creating a duplicate link
        # import six
        # import sys
        # if not six.PY2 and sys.platform.startswith('win32'):
        dirstats(dpath)
        ub.symlink(happy_fpath, happy_flink, verbose=verbose)

        dirstats(dpath)
        with pytest.raises(Exception):  # file exists error
            ub.symlink(other_fpath, happy_flink, verbose=verbose)

        ub.symlink(other_fpath, happy_flink, verbose=verbose, overwrite=True)

        ub.delete(other_fpath, verbose=verbose)
        with pytest.raises(Exception):  # file exists error
            ub.symlink(happy_fpath, happy_flink, verbose=verbose)
        ub.symlink(happy_fpath, happy_flink, verbose=verbose, overwrite=True)


if __name__ == '__main__':
    r"""
    CommandLine:
        set PYTHONPATH=%PYTHONPATH%;C:/Users/erote/code/ubelt/ubelt/tests
        pytest ubelt/tests/test_links.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)