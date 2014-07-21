#!/bin/csh

# Usage ./precip6.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>


echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./precip6.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set inFile = $3 



set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set MODEL_PATH  = $4 

set variable = "precip6"

set baseDir = "data"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -r ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

 set imgDir = ${baseDir}/${model}/${timeStamp}/sfc/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/sfc/${variable}

 gdplot_gf << EOF 
         
  GDFILE  = "${MODEL_PATH}/${model}/${inFile}"
  GDATTIM = "f${TIME}"
  GLEVEL  = 0 
  GVCORD  = none 
  PANEL   = 0 
  SKIP    = 
  SCALE   = 0 
  GFUNC   = p06i 
  CTYPE   = c/f
  CONTUR  = 1 
  CINT    = 0.25;0.5;0.75;1;1.5;2.0;3.0
  TYPE    = c/f
  LINE    = 16/10/1/1 
  FINT    = 0.01;0.1;0.25;0.5;0.75;1;1.5;2.0;3.0
  FLINE   = 0;21;22;23;20;17;15;2;7 
  HILO    = 
  HLSYM   = 
  GVECT   = 
  WIND    = bm32/0.8 
  REFVEC  = 
  GAREA   = 19.00;-119.00;50.00;-56.00
  PROJ    = STR/90;-100;0
  CLEAR   = yes 
  MAP     = 0
  TITLE   = 
  DEVICE  = "gif|init_${model}_sfc_${variable}_f${TIME}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts
 # convert to a transparent image layer.
 convert init_${model}_sfc_${variable}_f${TIME}.gif -transparent black ${imgDir}/f${TIME}.gif
 rm init_${model}_sfc_${variable}_f${TIME}.gif


end