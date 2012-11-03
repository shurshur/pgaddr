Simple PostGIS address extration tool
=====================================

This tool extracts addresses of all building inside given boundary from Gis-Lab PostGIS

Usage:

	./pgaddr [-k] <ID-of-boundary>

E.g.

	./pgaddr.py -1029489 > murmansk.csv
	./pgaddr.py -k -1029489 > murmansk-karlsruhe-only.csv

