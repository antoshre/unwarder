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

parser.add_option("--dirtocalypse", dest="dirtocalypse",
		  action="store_true", default=False,
		  help="Replace warded blocks with dirt")

parser.add_option("-v","--verbose", dest="verbose",
		  action="store_true", default=False,
		  help="Verbose log")

(options,args) = parser.parse_args()

if options.xc is None:
  parser.error("xc required")
if options.zc is None:
  parser.error("zc required")
if options.pathname is None:
  parser.error("world path required")
if options.verbose is False:
  options.logLevel = logging.INFO
else:
  options.logLevel = logging.DEBUG

logging.basicConfig(level=options.logLevel,
                    filename="unwarder.log",
                    format="%(asctime)s - %(levelname)s: %(message)s",
                    datefmt='%I:%M:%S %p',
                    filemode='w')
logger = logging.getLogger('unwarder')
logger.info("\tLog Start")
logger.debug("Options supplied:\n\t%s", options)

#Load level
try:
  level = mclevel.fromFile(options.pathname)
except IOError:
  sys.exit("IO error, check the path")

logger.debug("Loaded level \"%s\", ",level.LevelName)
    
#Load chunk
try:
  chunk = level.getChunk(options.xc,options.zc)
except ChunkNotPresent:
  sys.exit("Chunk not present")
logger.debug("Loaded chunk %s",chunk.chunkPosition)

if chunk is None:
  sys.exit("Chunk is 'None', how did you do that?")

wTE = namedtuple('wardedTE','x y z bID meta owner entity')

TElist = []
for entity in chunk.TileEntities: #for all entities in the chunk:
  if entity["id"].value == u'TileWarded': #is it a warded entity?
    if "bi" in entity:	#Does it have a blockid value?  (sanity check)
      if "md" in entity:  #Does it have a meta value? (sanity check)
        TElist.append( wTE(entity["x"].value, entity["y"].value, entity["z"].value, #unpack to named tuple to make access easier
			   entity["bi"].value, entity["md"].value, entity["owner"].value, entity))
        
logger.info("%d warded TEs found", len(TElist))

if len(TElist) == 0:
  sys.exit("No warded TileEntites detected")

for entity in TElist: #for every wardedTE:
  logger.debug("%s",entity)
  
  if entity.bID < 0:
    sys.exit("bID out of range")
  if entity.meta < 0 or entity.meta > 16:
    sys.exit("meta out of range")
    
  xOffset = entity.x % 16
  zOffset = entity.z % 16
  #y offset not required
  
  #ID 4035 is the faked ID of a warded block.
  if chunk.Blocks[xOffset,zOffset,entity.y] != 4035:
    sys.exit("Block pointed at be wTE isn't warded fakeID")
  
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
    logger.info("Wrote bID:meta %s to (x,y,z): %s",bIDTo,meta,(entity.x,entity.y,entity.z))
      
    #Remove the entities
    chunk.TileEntities.remove(entity.entity)
#end for

if not options.dryrun:
  logger.info("Writing to disk")
  #Mark as changed
  logger.debug("\tMark chunk as changed")
  chunk.chunkChanged()
  #Update lighting, probably not necessary
  logger.debug("\tGenerate lights")
  level.generateLights()
  #Save.
  logger.debug("\tSave")
  level.saveInPlace()
  logger.debug("Save complete")