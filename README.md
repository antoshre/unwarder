unwarder
========

Unwards a chunk

Filename of level is hard-coded.  Couldn't find a way to read in as an argument without breaking spaces and whatnot.  Must be changed to do anything useful.

'dryrun' at the top of the file changes whether it attempts to actually unward blocks.

****
##Usage

>python unwarder.py <xPos> <zPos>

####Example:

Say I want to unward a chunk that contains the block 700,600.

>python unwarder.py 700 600

****
unwarder.log is the log file. In the event of an error it may help track exactly where the process went wrong.