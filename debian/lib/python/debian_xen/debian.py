import re
from debian_linux.debian import Version


class VersionXen(Version):
    _version_xen_rules = r"""
        ^
        (?P<version>\d+\.\d+)
        (?:
         \.\d+(?:~pre(?:\+\d+\.(?P<pre_commit>[0-9a-f]{10})))?
         |
         ~rc\d+(?:\+\d+\.(?P<rc_commit>[0-9a-f]{10}))?
        )
        -
        (?:[^-]+)
        $
        """
    _version_xen_re = re.compile(_version_xen_rules, re.X)

    def __init__(self, version):
        super(VersionXen, self).__init__(version)
        match = self._version_xen_re.match(version)
        if match is None:
            raise ValueError("Invalid debian xen version")
        d = match.groupdict()
        self.xen_version = d['version']
        self.pre_commit = d['pre_commit']
        self.rc_commit = d['rc_commit']
