#
# EZ250
#
# This script will plot the 250 mb isotachs, heights and winds for
# all of the times for the given model.
#
# Syntax: ez250
#
##
# Log:
# D. Plummer/NMC 1994
# S. Jacobs/NMC 10/94 Clean up

#!/bin/bash

.  /home/cacraig/gempak/GEMPAK7/Gemenviron.profile

## Change GEMPAK6.2.0/os/darwin/bin to your ${NAWIPS}/os/darwin/bin
#PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/X11/bin:/${NAWIPS}/os/darwin/bin

variable="RELH"
name="relh_850mb"
level="850"

gdplot << EOF 
         
 GDFILE   = $MODEL/gfs/2014021912_gfs.gem
 GDATTIM  = f012
 CLEAR    = y
 GLEVEL   = ${level}
 GVCORD   = pres
 PANEL    = 0
 SKIP     =  
 SCALE    = 5
 GFUNC    = QUO(${variable}, 100000)
 CTYPE    = f
 CONTUR   = 2
 CINT     = 2
 LINE     = 1/1
 !FINT     = 10;12;14;16;18;20;22;24
 !FLINE    = 101;21;22;23;5;19;17;16;15;5
 fint=0;20;30;40;50;60;70;80;90;100
 fline=0;0;0;4;26;31;22;20;17;16;15
 HILO     =  
 HLSYM    =  
 CLRBAR   = 31/V/LL/
 GVECT    =  
 WIND     = 0
 REFVEC   =  
 TITLE    = 31/-2/GFS ~
 TEXT     = 1/2//hw
 GAREA    = us  
 IJSKIP   = 0
 PROJ     = str/90;-100;0
 MAP      = 0
 !BORDER   = 0/1/1
 !BND = 0
 MSCALE   = 0
 LATLON   = 0
 STNPLT   =  
 DEVICE = gif|gfs_${name}_init.gif|1280;1024| C
 run
exit
EOF

# clean output buffer/gifs, and cleanup
gpend
rm last.nts
rm gemglb.nts
# convert to a transparent image layer.
convert gfs_${name}_init.gif -transparent black gfs_${name}.gif
rm gfs_${name}_init.gif
