#!/bin/csh

# Usage ./pmsl.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>


echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./pmsl.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 



set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set MODEL_PATH  = $4 

set variable = "pmsl"

set baseDir = "data"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 

if (${model} == 'nam12km') then
  set extension = "_nam218.gem"
endif

if (${model} == 'nam4km') then
  set extension = "_nam4km.gem"
endif

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)
 # Reset line color!
 set lineColor = 13
 set level = 1000
 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}

 if (${model} == "nam12km") then
   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 endif 

  if (${model} == "nam4km") then
   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 endif 


 if (${model} == "ecmwf") then
  @ lineColor = $lineColor
 endif

 if (${model} == "nam12km") then
   @ lineColor = $lineColor + 1
 endif


if (${model} == "gfs") then
  @ lineColor = $lineColor + 2
endif

if (${model} == "ruc") then
  @ lineColor = $lineColor + 3
endif

if (${model} == "ukmet") then
  @ lineColor = $lineColor + 3
 endif

 gdplot2 << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${runTime}f${TIME}${extension}"
  GDATTIM  = "f${TIME}"
  GLEVEL   = "0"
  GVCORD   = "none"
  PANEL    = "0"
  GDPFUN   = sm9s(pmsl)
  HILO     =  
  HLSYM    =  
  CLEAR    = yes
  PANEL    = 0
  SCALE    = 0
  TYPE     = c
  CONTUR   = 1                                                                       
  CINT     = 4
  LINE     = "${lineColor}/1/2"
  GVECT    = 
  CLRBAR   = 
  SKIP     =  0
  TITLE    = 
  FINT     = 
  FLINE    = 
  CTYPE    = c
  GRDLBL   = 5                                                                       
  LUTFIL   = none
  FILTER   = no
  WIND     = "0"
  REFVEC   =  
  TEXT     = 
  IJSKIP   = "0"
  GAREA    = "19.00;-119.00;50.00;-56.00"
  PROJ     = "STR/90;-100;0"
  MAP      = "0"
  MSCALE   = "0"
  LATLON   = 
  STNPLT   =  
  DEVICE   = "gif|init_${model}_1000_${variable}_f${shortTime}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts
 # convert to a transparent image layer.
 convert init_${model}_1000_${variable}_f${shortTime}.gif -transparent black ${imgDir}/f${shortTime}.gif
 rm init_${model}_1000_${variable}_f${shortTime}.gif


end