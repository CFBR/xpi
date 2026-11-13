# version.py: the xpi release version.
#
# The version follows semantic versioning, MAJOR.MINOR.PATCH. Bump MAJOR for a
# breaking change, MINOR for a new feature, and PATCH for a fix. This is the
# only place the version is written; server.py imports it and the page reads it
# from /action=status.

import re

__version__ = "2.8.4"

_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_match = _SEMVER.match(__version__)
if _match is None:
    raise ValueError("xpi version is not semver: %r" % __version__)

MAJOR, MINOR, PATCH = (int(part) for part in _match.groups())
