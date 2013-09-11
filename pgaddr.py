#!/usr/bin/python
# vim:encoding=utf-8:shiftwidth=2:autoindent
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 
import psycopg2
from psycopg2.extras import register_hstore
from config import *

try:
  import psyco
  psyco.full()
except ImportError:
  pass

pg = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (postgis_data,postgis_user,postgis_host,postgis_pass))

cc = pg.cursor()
register_hstore(cc)

def usage():
  print ("""Export OSM addresses from Gis-Lab PostGIS
(c) Alexandr Zeinalov, 2011-2012

Usage: pgaddr [OPTIONS] BOUNDARY > FILE.csv

  BOUNDARY  - ID of bounadry way or
              negative ID of boundary relation

Options:

  -k        - Get names from Karlsruhe tags only
              (default: from Karlsruhe and administrative boundaries)

""")
  sys.exit(0)

args = []
karl = 0

for arg in sys.argv[1:]:
  if arg == '-k':
    karl = 1
  else:
    args.append(arg)

try:
  bnd_id = int(args[0])
except:
  usage()

if karl:
  q="SELECT '%%s',a.osm_id,%%s,a.name,a.tags->'addr:postcode',a.tags->'addr:region',a.tags->'addr:district',a.tags->'addr:city',a.tags->'addr:street',a.\"addr:housenumber\",1 FROM %%s a LEFT JOIN osm_polygon b ON ST_Within(a.way,b.way) WHERE a.\"addr:housenumber\" IS NOT NULL AND b.osm_id='%s'" % (bnd_id)
  q = (q % ("way", "ST_Y(ST_Centroid(a.way)),ST_X(ST_Centroid(a.way))", "osm_polygon")) + " UNION " + (q % ("node", "ST_Y(a.way),ST_X(a.way)", "osm_point"))
else:
  q="SELECT '%%s',a.osm_id,%%s,MIN(a.name),MIN(a.tags->'addr:postcode'),MIN(a.tags->'addr:region'),MIN(a.tags->'addr:district'),MIN(a.tags->'addr:city'),MIN(a.tags->'addr:street'),MIN(a.\"addr:housenumber\"),ARRAY_AGG(c.admin_level || ':' || c.name) FROM %%s a LEFT JOIN osm_polygon b ON ST_Within(a.way,b.way) LEFT JOIN osm_polygon c ON ST_Intersects(a.way,c.way) WHERE a.\"addr:housenumber\" IS NOT NULL AND b.osm_id='%s' AND c.admin_level IN ('2','4','5','6','7','8','9','10') GROUP BY a.osm_id" % (bnd_id)
  q = (q % ("way", "ST_Y(ST_Centroid(MIN(a.way))),ST_X(ST_Centroid(MIN(a.way)))", "osm_polygon")) + " UNION " + (q % ("node", "ST_Y(MIN(a.way)),ST_X(MIN(a.way))", "osm_point"))
#print >>sys.stderr, "Running Query: " + q
cc.execute(q)

#print '"type";"id";"lat";"lon";"name";"addr:postcode";"addr:region";"addr_district";"addr:city";"addr:street";"addr:housenumber"'
print ("Тип;ID;Долгота;Широта;Название;\"Почтовый индекс\";\"Регион\";\"Район\";\"Город/поселение\";\"Улица\";\"Дом\"")

while True:
  row = cc.fetchone()
  if not row:
    break
  type,osm_id,lat,lon,name,addr_postcode,addr_region,addr_district,addr_city,addr_street,addr_housenumber, _regs = row
  if type == "way" and osm_id<0:
    type = "relation"
    osm_id = -osm_id
  if not karl:
    regs = {}
    for i in _regs:
      tmp = i.split(":")
      al = int(tmp[0])
      rname = ":".join(tmp[1:])
      regs[al] = rname
    if not addr_region:
      try:
        addr_region = regs[4]
      except KeyError:
        addr_region = ""
    if not addr_district:
      try:
        addr_district = regs[6]
      except KeyError:
        addr_district = ""
    if not addr_city:
      try:
        addr_city = regs[8]
      except KeyError:
        addr_city = ""
  if not name:
    name = ""
  if not addr_postcode:
    addr_postcode = ""
  if not addr_street:
    addr_street = ""
  if not addr_housenumber:
    addr_housenumber = ""
  print ('"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s"' % (type,osm_id,lat,lon,name,addr_postcode,addr_region,addr_district,addr_city,addr_street,addr_housenumber))

