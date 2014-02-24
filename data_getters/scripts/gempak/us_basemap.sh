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
         
 GDFILE   = $MODEL/gfs/2014021912_gfs.gem
 GDATTIM  = f012
 PARM=
 CLEAR    = y
 GLEVEL   = 500
 GVCORD   = 
 PANEL    = 0
 SKIP     =  
 SCALE    = 5
 CTYPE    = f
 CONTUR   = 2
 CINT     = 2
 LINE     = 1/1
 fint=-15
 fline=10
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
 MAP     = 32
 MSCALE   = 0
 LATLON   = 0
 STNPLT   =  
 BND = 0/1/1
 BORDER = 0
 COLORS   =32
 DEVICE = gif|US_basemap.gif|800;600| C
 run
exit
EOF

# clean output buffer/gifs, and cleanup
gpend
rm last.nts
rm gemglb.nts 
