"""Sample file showing the expected format for db_credentials.py"""

# --- CONTENTS START ---

"""Login credentials for MySQL"""

username = 'root'
password = 'Noshu@1211'
host = 'localhost'
db_name = 'y2k_database>'

# --- CONTENTS END ---

"""
Note: If you do wanna test this out, do NOT use the same `db_name` as the current
(PyMySQL implementation) as table structures are different in the new implementation.
Also, ensure (for now) that the database already exists before running this file.

For now no functionality really changes. All you can verify is that the tables are
created (check `models.py` for info about the tables being set up). Will change
all existing SQL commands to make it work soon. That's secondary for now though.
"""
