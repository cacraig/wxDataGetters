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

#! /bin/bash

.  /home/cacraig/gempak/GEMPAK7/Gemenviron.profile

## Change GEMPAK6.2.0/os/darwin/bin to your ${NAWIPS}/os/darwin/bin
#PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/X11/bin:/${NAWIPS}/os/darwin/bin

gdplot << EOF 
         
 GDFILE   = $MODEL/gfs/2014022300_gfs211.gem
 GDATTIM  = f012
 CLEAR    = y
 GLEVEL   = 500
 GVCORD   = pres
 PANEL    = 0
 SKIP     =  
 SCALE    = 999
 GFUNC    = hght
 CTYPE    = c
 CONTUR   = 3/3
 CINT     = 0
 LINE     = 3/1/3
 !FINT     = 10;12;14;16;18;20;22;24
 !FLINE    = 101;21;22;23;5;19;17;16;15;5
 fint=-15;-12;-9;-6;-3;3;6;9;12;15 
 fline=7;30;24;4;26;31;22;20;17;16;15
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
 DEVICE = gif|gfs_hght_500mb_init.gif|1280;1024| C
 run
exit
EOF

# clean output buffer/gifs, and cleanup
gpend
rm last.nts
rm gemglb.nts
# convert to a transparent image layer.
convert gfs_hght_500mb_init.gif -transparent black gfs_hght_500mb.gif
rm gfs_hght_500mb_init.gif
