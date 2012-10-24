#!/usr/bin/python
# vim:encoding=utf-8:shiftwidth=2:autoindent
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 
import psycopg2
from config import *

try:
  import psyco
  psyco.full()
except ImportError:
  pass

#typeof = type

pg = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (postgis_data,postgis_user,postgis_host,postgis_pass))

cc = pg.cursor()

def usage():
  print """Export OSM addresses from Gis-Lab PostGIS
(c) Alexandr Zeinalov, 2011-2012

Usage: pgaddr BOUNDARY > FILE.csv

  BOUNDARY  - ID of bounadry way or
              negative ID of boundary relation
"""
  sys.exit(0)

try:
  bnd_id = sys.argv[1]
except:
  usage()

q="SELECT '%%s',a.osm_id,%%s,a.name,a.tags->'addr:postcode',a.tags->'addr:region',a.tags->'addr:district',a.tags->'addr:city',a.tags->'addr:street',a.\"addr:housenumber\" FROM %%s a LEFT JOIN osm_polygon b ON ST_Within(a.way,b.way) WHERE a.\"addr:housenumber\" IS NOT NULL AND b.osm_id='%s'" % (bnd_id)
#print q
q = (q % ("way", "ST_Y(ST_Centroid(a.way)),ST_X(ST_Centroid(a.way))", "osm_polygon")) + " UNION " + (q % ("node", "ST_Y(a.way),ST_X(a.way)", "osm_point"))
#print q
cc.execute(q)

print '"type";"id";"lat";"lon";"name";"addr:postcode";"addr:region";"addr_district";"addr:city";"addr:street";"addr:housenumber"'

while True:
  row = cc.fetchone()
  if not row:
    break
  type,osm_id,lat,lon,name,addr_postcode,addr_region,addr_district,addr_city,addr_street,addr_housenumber = row
  print ('"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s"' % (type,osm_id,lat,lon,name,addr_postcode,addr_region,addr_district,addr_city,addr_street,addr_housenumber))


