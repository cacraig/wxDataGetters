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

gdcross << EOF 
         
 GDFILE   = $MODEL/ruc/2014022211_ruc236.gem
 CXSTNS   = lax>bwi
GDATTIM  = f006
GVCORD   = pres
GFUNC    = tmpk
GVECT    = wnd
GDFILE   = gfs
WIND     = bm32
REFVEC   = 10
PTYPE    = log
YAXIS    =  
IJSKIP   = 0
CINT     =  
SCALE    =  
LINE     = 32/1/3
BORDER   = 1
TITLE    = 1
CLEAR    = yes
DEVICE   = xw
TEXT     = 1
PANEL    = 0
CLRBAR   = 1/h/cc/.5;.03/.6;.01
CONTUR   = 3
FINT     = 5
FLINE    = 13-30
CTYPE    = f
 DEVICE = gif|test.gif|1280;1024| C
 run
exit
EOF

# clean output buffer/gifs, and cleanup
gpend
rm last.nts
rm gemglb.nts
# convert to a transparent image layer.
