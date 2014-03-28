import sys
import logging
from optparse import OptionParser
from pymclevel import *

usage = "usage: %prog [OPTIONS]\n\t Example: %prog -x 100 -z 100 -f \"~/level.dat\""
parser = OptionParser(usage)
parser.add_option("-x","--xPos", dest="xPos",metavar="XPOS",
		  action="store", type="int",
		  help="X coordinate for target chunk")

parser.add_option("-z","--zPos", dest="zPos", metavar="ZPOS",
		  action="store", type="int",
		  help="Z coordinate for target chunk")

parser.add_option("-f","--file", dest="filename", metavar="FILE",
		  action="store", type="string",
		  help="Filename of level.dat")

parser.add_option("--commit", dest="dryrun", default=True,
		  action="store_false",
		  help="Write changes to disk")

parser.add_option("--dirtocalypse", dest="dirtocalypse", default=False,
		  action="store_true",
		  help="Replace warded blocks with dirt")

(options,args) = parser.parse_args()

if options.xPos is None or options.zPos is None or options.filename is None:
  sys.exit("Argument parse error")

logging.basicConfig(level=logging.DEBUG, filename="unwarder.log",format="%(asctime)s - %(levelname)s: %(message)s", datefmt='%I:%M:%S %p', filemode='w')
logging.debug("\tLog Start")

logging.debug("Options supplied:")
logging.debug("xPos: %d zPos: %d dryrun: %r filename: %s",options.xPos,options.zPos,options.dryrun,options.filename)

if options.dryrun:
  logging.info("Dry run enabled, no changes will be written.") 
else:
  logging.info("!!! Not a dry run!  Will be writing to disk!")
#Load level
try:
  level = mclevel.fromFile(options.filename)
except IOError:
  logging.debug("IO error on file opening.  Fuck.  Check the path.")
  sys.exit("IO error")
    
#Load chunk
try:
  chunk = level.getChunk(options.xPos/16,options.zPos/16)
except ChunkNotPresent:
  logging.debug("chunk not preset?! x: %d z: %d",options.xPos,options.zPos)
  sys.exit("Chunk not present error")

if chunk is None:
  logging.warn("chunk is None. How the fuck-")
  sys.exit("chunk is none?")

#ID 4035 warded shit

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

wardedTE = []
for entity in chunk.TileEntities:
  if entity["id"].value == u'TileWarded':
    if "bi" in entity:
      if "md" in entity:
        wardedTE.append(entity)
        
logging.debug("%d warded TileEntites found.", len(wardedTE))

if len(wardedTE) == 0:
  sys.exit("No warded TileEntites detected")

for entity in wardedTE:
  logging.debug("TE @ x: %d y: %d z: %d",entity["x"].value,entity["y"].value,entity["z"].value)
  logging.debug("\tbId: %d meta: %d",entity["bi"].value,entity["md"].value)
  
  if entity["bi"].value < 0:
    logging.warning("bId out of range!")
    sys.exit("bId out of range")
  if entity["md"].value < 0 or entity["md"].value > 16:
    logging.warning("meta out of range!")
    sys.exit("meta out of range")
  
  xOffset = entity["x"].value % 16
  zOffset = entity["z"].value % 16
  #y offset not required
  
  if chunk.Blocks[xOffset,zOffset,entity["y"].value] != 4035:
    logging.warning("\tBlock not the fake warded ID!")
    sys.exit("ID isn't fake warded")
  logging.debug("\tBlock matches fake warded ID, ready to be replaced")
  
  
  if not options.dryrun:
    #Change the blocks
    if options.dirtocalypse:
      dirtID = level.materials["Dirt"].ID
      dirtMeta = level.materials["Dirt"].blockData
      chunk.Blocks[xOffset,zOffset,entity["y"].value] = dirtID
      chunk.Data[xOffset,zOffset,entity["y"].value] = dirtMeta
      logging.debug("\tWrote bi: %d md: %d", dirtID, dirtMeta)
    else:
      chunk.Blocks[xOffset,zOffset,entity["y"].value] = entity["bi"].value
      chunk.Data[xOffset,zOffset,entity["y"].value] = entity["md"].value
      logging.debug("\tWrote bi: %d md: %d",entity["bi"].value,entity["md"].value)
      
    #Remove the entities
    chunk.TileEntities.remove(entity)
    #Mark as changed for compression and saving
    chunk.chunkChanged()
    level.generateLights()
    #Save
    level.saveInPlace()