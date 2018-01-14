#!/usr/bin/env python3

import sys
sys.path.append(sys.path[0] + '/../lib/python')

import itertools
import os, os.path
import shutil
import subprocess

from debian_xen.debian import VersionXen
from debian_linux.debian import Changelog


class Main(object):
    log = sys.stdout.write

    def __init__(self, options, repo):
        self.options = options
        self.repo = repo

        self.changelog_entry = Changelog(version=VersionXen)[0]
        self.source = self.changelog_entry.source
        self.version = self.changelog_entry.version

        if options.override_version:
            self.version = VersionXen('%s-0' % options.override_version)

        if options.component:
            self.orig_dir = options.component
            self.orig_tar = '%s_%s.orig-%s.tar.xz' % (self.source, self.version.upstream, options.component)
        else:
            self.orig_dir = '%s-%s' % (self.source, self.version.upstream)
            self.orig_tar = '%s_%s.orig.tar.xz' % (self.source, self.version.upstream)

    def __call__(self):
        gitout = "../orig/gitout_%s" % self.orig_tar
        out = "../orig/%s" % self.orig_tar
        self.log("Generate tarball %s\n" % gitout)

        if self.options.tag:
            treeish = self.options.tag
        else:
            if self.changelog_entry.version.pre_commit:
                treeish = self.changelog_entry.version.pre_commit
            elif self.changelog_entry.version.rc_commit:
                treeish = self.changelog_entry.version.rc_commit
            else:
                treeish = 'RELEASE-%s' % self.version.upstream

        try:
            os.stat(out)
            raise RuntimeError("Destination already exists")
        except OSError: pass

        #export from git
        try:
            with open(gitout, 'wb') as f:
                _cmd = ('git', 'archive', '--prefix', '%s/' % self.orig_dir, treeish)
                p1 = subprocess.Popen(_cmd, stdout=subprocess.PIPE, cwd=self.repo)
                subprocess.check_call(('xz', ), stdin=p1.stdout, stdout=f)
                if p1.wait():
                    raise RuntimeError
        except:
            os.unlink(out)
            raise
        #unpack
        self.log("unpack tarball %s\n" % gitout)

        _cmd = ('tar', '-xf', gitout)
        subprocess.call(_cmd, cwd="../orig/")

        self.log("fetch files \n" )
        subprocess.call(('ls', '-lhtr'), cwd='../orig/%s' % self.orig_dir)
        subprocess.call(('make', 'mini-os-dir'), cwd='../orig/%s' % self.orig_dir)  
        tars = ["gmp-4.3.2.tar.bz2", "grub-0.97.tar.gz",  "lwip-1.3.0.tar.gz",  "newlib-1.16.0.tar.gz",  "pciutils-2.2.9.tar.bz2",  "tpm_emulator-0.7.4.tar.gz",  "zlib-1.2.3.tar.gz"]
        subprocess.call(('./configure'), cwd='../orig/%s/stubdom' % self.orig_dir)
        for tar in tars:
            subprocess.call(('make', tar), cwd='../orig/%s/stubdom' % self.orig_dir)

        self.log("pack again \n" )
        subprocess.call(('tar','--xz','-cvf', out, self.orig_dir), cwd='../orig/')

        try:
            os.symlink(os.path.join('orig', self.orig_tar), os.path.join('..', self.orig_tar))
        except OSError:
            pass


if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser(prog=sys.argv[0], usage='%prog [OPTION]... DIR')
    p.add_option('-c', '--component', dest='component')
    p.add_option('-t', '--tag', dest='tag')
    p.add_option('-V', '--override-version', dest='override_version')
    options, args = p.parse_args()
    if len(args) != 1:
        raise RuntimeError
    Main(options, *args)()
