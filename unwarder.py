import sys
import logging
from optparse import OptionParser
from pymclevel import *
from collections import namedtuple

usage = "usage: %prog [OPTIONS]\n\t Example: %prog -x 1 -z -1 -p \"/minecraft/saves/worldFolder/\""
parser = OptionParser(usage)
parser.add_option("-x","--xchunk", dest="xc",metavar="XC",
		  action="store", type="int",
		  help="xc of chunk coord (xc,zc)")

parser.add_option("-z","--zchunk", dest="zc", metavar="ZC",
		  action="store", type="int",
		  help="zc of chunk coord (xc,zc)")

parser.add_option("-p","--path", dest="pathname", metavar="PATH",
		  action="store", type="string",
		  help="Path of directory containing level.dat")

parser.add_option("--commit", dest="dryrun", default=True,
		  action="store_false",
		  help="Write changes to disk")

parser.add_option("--dirtocalypse", dest="dirtocalypse", default=False,
		  action="store_true",
		  help="Replace warded blocks with dirt")

(options,args) = parser.parse_args()

if options.xc is None:
  parser.error("xc required")
if options.zc is None:
  parser.error("zc required")
if options.pathname is None:
  parser.error("world path required")

logging.basicConfig(level=logging.DEBUG, filename="unwarder.log",format="%(asctime)s - %(levelname)s: %(message)s", datefmt='%I:%M:%S %p', filemode='w')
logging.debug("\tLog Start")

logging.debug("Options supplied:")
logging.debug("xc: %d zc: %d dryrun: %r path: %s",options.xc,options.zc,options.dryrun,options.pathname)

if options.dryrun:
  logging.info("Dry run enabled, no changes will be written.") 
  print "Dry run enabled."
else:
  logging.info("!!! Not a dry run!  Will be writing to disk!")
  print "Dry run disabled.\n[!]Changes will be committed to disk[!]"
#Load level
try:
  level = mclevel.fromFile(options.pathname)
except IOError:
  logging.debug("IO error on file opening. Double-check the path.")
  sys.exit("IO error")
    
#Load chunk
try:
  chunk = level.getChunk(options.xc,options.zc)
except ChunkNotPresent:
  logging.debug("Chunk not present")
  sys.exit("Chunk not present")

if chunk is None:
  logging.warn("chunk is None. How the fu-")
  sys.exit("chunk is none?!")

#ID 4035 warded block ID

""" Find all TileEntities associated with warded blocks
  "id" = u'TileWarded'
  "ll" = ?
  "md" = TAG_Int, meta of original
  "owner" = owner of block
  "bi" = TAG_Int, block id of original
  "x" = TAG_Int, x location
  "y" = TAG_Int, y location
  "z" = TAG_Int, z location
"""

wardedTE = namedtuple('wardedTE','x y z bID meta owner entity')

TElist = []

for entity in chunk.TileEntities: #for all entities in the chunk:
  if entity["id"].value == u'TileWarded': #is it a warded entity?
    if "bi" in entity:	#Does it have a blockid value?  (sanity check)
      if "md" in entity:  #Does it have a meta value? (sanity check)
        TElist.append( wardedTE(entity["x"].value, entity["y"].value, entity["z"].value,
				entity["bi"].value, entity["md"].value, entity["owner"].value,entity))
        
logging.debug("%d warded TEs found", len(TElist))


if len(TElist) == 0:
  sys.exit("No warded TileEntites detected")
else:
  print "%d warded TEs found" % len(TElist)

for entity in TElist: #for all entities in the list:
  
  logging.debug("TE @ x: %d y: %d z: %d", entity.x, entity.y, entity.z)
  logging.debug("\t bID: %d meta: %d owner: %s", entity.bID, entity.meta, entity.owner)
  
  if entity.bID < 0:
    logging.warning("\tbID out of range!")
    sys.exit("bID out of range")
  if entity.meta < 0 or entity.meta > 16:
    logging.warning("\tmeta out of range!")
    sys.exit("meta out of range")
    
  xOffset = entity.x % 16
  zOffset = entity.z % 16
  #y offset not required
  
  if chunk.Blocks[xOffset,zOffset,entity.y] != 4035:
    logging.warning("\tBlock not the fake warded ID!")
    sys.exit("ID isn't fake warded")
  logging.debug("\tBlock matches fake warded ID, ready to be replaced")
  
  
  if not options.dryrun:
    #Change the blocks
    
    if options.dirtocalypse:
      bIDTo = level.materials["Dirt"].ID
      metaTo = level.materials["Dirt"].blockData
    else:
      bIDTo = entity.bID
      metaTo = entity.meta
    
    chunk.Blocks[xOffset,zOffset,entity.y] = bIDTo
    chunk.Data[xOffset,zOffset,entity.y] = metaTo
    logging.debug("\tWrote bi: %d md: %d",bIDTo, metaTo)
      
    #Remove the entities
    chunk.TileEntities.remove(entity.entity)
    
    #Mark as changed for compression and saving
    chunk.chunkChanged()
    level.generateLights()
    #Save
    level.saveInPlace()
    
print "Done"