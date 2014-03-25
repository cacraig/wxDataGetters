#!/bin/csh

# Usage ./wind.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>


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

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
endif

#Default barb/color width
set barbColor = 31

set variable = "barbs"


foreach TIME ($times:q)

foreach level (250 500 850 1000)

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 
 if (${level} == 250) then
   set barbColor = 28
 endif

 if (${level} == 500) then
   set barbColor = 21
 endif

 if (${level} == 850) then
   set barbColor = 17
 endif

 if (${level} == 1000) then
   set barbColor = 13
 endif

 if (${model} == "ecmwf") then
  @ barbColor = $barbColor
 endif

 if (${model} == "nam") then
   @ barbColor = $barbColor + 1
 endif


 if (${model} == "gfs") then
  @ barbColor = $barbColor + 2
 endif

 if (${model} == "ruc") then
  @ barbColor = $barbColor + 3
 endif

if (${model} == "ukmet") then
  @ barbColor = $barbColor + 3
 endif

 

 gdplot << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${inFile}"
  GDATTIM  = "f${TIME}"
  CLEAR    = "n"
  GLEVEL   = "${level}"
  GVCORD   = "PRES"
  PANEL    = "0"
  SKIP  =  "1/2"  
  SCALE =  "0"                                                              
  GFUNC =                                             
  CTYPE =                                                                    
  CONTUR =      
  GVECT = "WND"
  WIND = "bm${barbColor}//2"                                                         
  CINT   =                                       
  LINE   =                                                
  FINT   =                                                   
  FLINE  = 
  HILO   =                                                                    
  HLSYM  =                                                                        
  REFVEC =       
  TITLE =                                                                       
  CLEAR =  "yes"
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
 convert init_f${TIME}.gif -transparent black ${imgDir}/f${TIME}.gif
 rm init_f${TIME}.gif

 end

end
