unwarder
========

Unwards a chunk

**REQUIRES pymclevel somewhere in your path.**

****
##Usage

>python unwarder.py -x [XPOS] -z [ZPOS] -f [FILE] \(--commit\)

####Example:

Say I want to see all warded blocks in the chunk that contains the block 700,600 in a world whose level.dat is located at ~/Herp/Derp/level.dat

>python unwarder.py -x 700 -z 600 -f "~/Herp/Derp"

This will not write anything to the world, merely dumping contents into the log.

Looked over the log and nothing looks wrong?

>python unwarder.py -x 700 -z 600 -f "~/Herp/Derp" --commit

****
unwarder.log is the log file. In the event of an error it may help track exactly where the process went wrong.