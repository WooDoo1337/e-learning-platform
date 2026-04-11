"""
Work around django-redisboard 9.0.0 bugs in RedisServerStats.databases:

- Keys like db0_distrib_* are skipped; only db0, db1, … (regex ^db\\d+$).
- The stock 9.0.0 code uses ``for db in (name[2:])``, which iterates *characters*,
  so a leading digit in db0_foo is mistaken for a db id and the value (often str)
  breaks on ``.items()``.

Call ``apply_redisboard_db_fix()`` from an AppConfig.ready() after Django apps
are loaded (importing redisboard.models earlier raises AppRegistryNotReady).
"""
import re
from itertools import starmap

_RE_DB = re.compile(r'^db(\d+)$')

_applied = False


def apply_redisboard_db_fix() -> None:
    global _applied
    if _applied:
        return
    from redisboard.models import RedisServerStats
    from redisboard.models import coerce_detail
    from redisboard.utils import cached_property

    def _databases(self) -> dict[int, dict]:
        out: dict[int, dict] = {}
        for name, data in self.info.items():
            m = _RE_DB.match(name)
            if not m or not isinstance(data, dict):
                continue
            out[int(m.group(1))] = dict(starmap(coerce_detail, data.items()))
        return out

    prop = cached_property(_databases)
    prop.__set_name__(RedisServerStats, 'databases')
    RedisServerStats.databases = prop
    _applied = True
