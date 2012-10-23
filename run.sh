#!/bin/sh
python pgaddr.py -1029489 | iconv -f utf-8 -t cp1251//translit > murmansk.csv
