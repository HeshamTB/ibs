#!/bin/python

# Hesham T. Banafa
# Jun 12th, 2022
# Check enviorment file permissions and return -1 if fails or 0

import os
import stat

ENV_FILE='.env'

st = os.stat(ENV_FILE)
if st.st_mode & stat.S_IROTH or \
    st.st_mode & stat.S_IWOTH or \
    st.st_mode & stat.S_IXOTH:
    exit(1)

exit(0)