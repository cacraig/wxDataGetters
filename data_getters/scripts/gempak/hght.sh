#!/bin/csh

# Usage ./hght.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./avor.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set inFile = $3 

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set baseDir = "data"
set variable = "hght"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

foreach level (500 850)

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}

 gdplot << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${inFile}"
  GDATTIM  = "f${TIME}"
  CLEAR    = "n"
  GLEVEL   = "${level}"
  GVCORD   = "PRES"
  PANEL    = "0"
  SKIP     =  
  SCALE    = "-1"
  GFUNC    = "hght"
  CTYPE    = "c"
  CONTUR   = 
  CINT     = "8"
  LINE     = "3/1/2/1"
  HILO     =  
  HLSYM    =  
  CLRBAR   = 
  GVECT    =  
  WIND     = 
  REFVEC   =  
  TITLE    = 
  TEXT     = "1/21//hw"
  GAREA    = "us" 
  IJSKIP   = "0"
  PROJ     = 
  MAP      = "0"
  STNPLT   =
  DEVICE = "gif|init_f${TIME}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts
 # convert to a transparent image layer.
 convert init_f${TIME}.gif -transparent white ${imgDir}/f${TIME}.gif
 rm init_f${TIME}.gif

 end

end
