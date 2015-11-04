#!/bin/bash

export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
( cd /app/vphshare-dev/vphshare/masterinterface; python manage.py ejobsclean 7 )
