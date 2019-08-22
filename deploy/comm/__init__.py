#!/usr/bin/env python3

import sys
if sys.version_info.major == 3:
    import pymysql
    pymysql.install_as_MySQLdb()