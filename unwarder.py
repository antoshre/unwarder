dryrun = True #Don't actually change anything
#dryrun = False #Write changes to disk

import sys
sys.path.append("/home/rob/Downloads/") #Point to where the pymclevel folder is
from pymclevel import *

import logging
logging.basicConfig(level=logging.DEBUG, filename="unwarder.log",format="%(asctime)s - %(levelname)s: %(message)s", datefmt='%I:%M:%S %p', filemode='w')
logging.debug("\tLog Start")

logging.debug("Options supplied:")
logging.debug(sys.argv[1:])

if dryrun:
  logging.info("Dry run enabled, no changes will be written.")


if len(sys.argv) < 3:
  logging.debug("Too few options given")
  sys.exit("Too few arguments, expects two")
  
#Read in coordinates from terminal
#Chunk to target in world coordinates.
try:
  xPos = int(sys.argv[1])
  zPos = int(sys.argv[2])
except TypeError:
  logging.debug("TypeError when parsing arguments")
  sys.exit("Argument TypeError")
except ValueError:
  logging.debug("ValueError when parsing arguments")
  sys.exit("Argument ValueError")
 
 
#Load level
try:
  level = mclevel.fromFile("/home/rob/.technic/modpacks/goonimati-forge/saves/Flat (testing)/level.dat")
except IOError:
  logging.debug("IO error on file opening.  Fuck.")
  sys.exit("IO error")
  
#Load chunk
try:
  chunk = level.getChunk(xPos/16,zPos/16)
except ChunkNotPresent:
  logging.debug("chunk not preset?! x: %d z: %d",xPos,zPos)
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
  
  
  if not dryrun:
    chunk.Blocks[xOffset,zOffset,entity["y"].value] = entity["bi"].value
    chunk.Data[xOffset,zOffset,entity["y"].value] = entity["md"].value
    logging.debug("\tWrote bi: %d md: %d",entity["bi"].value,entity["md"].value)
    chunk.chunkChanged()
    level.saveInPlace()