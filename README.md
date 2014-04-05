unwarder
========

Unwards a chunk

****
```
Usage: unwarder.py [OPTIONS]
         Example: unwarder.py -x 1 -z -1 -p "/minecraft/saves/worldFolder/"

Options:
  -h, --help            show this help message and exit
  -x XC, --xchunk=XC    xc of chunk coord (xc,zc)
  -z ZC, --zchunk=ZC    zc of chunk coord (xc,zc)
  -p PATH, --path=PATH  Path of directory containing level.dat
  --commit              Write changes to disk
  --dirtocalypse        Replace warded blocks with dirt
  -v, --verbose         Verbose log
```

****
TODO:

Cleanup log stuff, streamline
  
  
##Example:

###Remove all warded blocks in chunk (5,6) from world located at "/home/user/.minecraft/saves/world1"

First, do a dryrun to see if anything goes wrong:  
>python unwarder.py -x 5 -z 6 -p "/home/user/.minecraft/saves/world1"

If no errors occur and the log looks good, commit:  
>python unwarder.py -x 5 -z 6 -p "/home/user/.minecraft/saves/world1" --commit

This should replace all warded blocks with their originals.  I am not responsible if this somehow destroys your world.  Backup **everything** beforehand.

###Replace all warded blocks by dirt:

Same as the first example, but use the `--dirtocalypse` flag.

****

The `-v` flag causes the script to dump nearly everything to the log.  If you have a lot of warded blocks this is going to get ugly fast but would be invaluable for debugging purposes.