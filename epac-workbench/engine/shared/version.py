"""Single source of truth for the engine version (#27).

SemVer, kept in lockstep with git tags. The value here is what the code *stamps*
into ``catalogue.json`` (``producedByEngine``) and each package's ``lineage.json``
(``engineVersion``) — a plain constant so those artifacts are byte-reproducible on
any checkout (no runtime ``git`` call, no CI shallow-clone fragility).

The number is not hand-picked: ``engine/tools/release.py`` derives the next SemVer
from Conventional-Commit prefixes since the last ``v*`` tag (``fix:`` -> patch,
``feat:`` -> minor, ``feat!:``/``BREAKING CHANGE`` -> major), then updates this
constant + ``pyproject.toml`` and creates the tag. So the tag and this string always
agree; ``git describe`` remains the human-facing release marker.
"""

__version__ = "0.2.0"
