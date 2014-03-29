unwarder
========

Unwards a chunk

****
Usage: unwarder.py [OPTIONS]  
         Example: unwarder.py -x 100 -z 100 -f "~/level.dat"

Options:
  -h, --help            show this help message and exit  
  -x XPOS, --xPos=XPOS  X coordinate for target chunk  
  -z ZPOS, --zPos=ZPOS  Z coordinate for target chunk  
  -f FILE, --file=FILE  Filename of level.dat  
  --commit              Write changes to disk  
  --dirtocalypse        Replace warded blocks with dirt  

####Example:

Say I want to see all warded blocks in the chunk that contains the block 700,600 in a world whose level.dat is located at /Herp/Derp/level.dat

>python unwarder.py -x 700 -z 600 -f "/Herp/Derp"

This will not write anything to the world, merely dumping contents into the log.

Looked over the log and nothing looks wrong?

>python unwarder.py -x 700 -z 600 -f "/Herp/Derp" --commit

****
unwarder.log is the log file. In the event of an error it may help track exactly where the process went wrong.
