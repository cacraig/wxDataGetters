#!/bin/csh

# Usage ./hght.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./rh.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set inFile = $3 

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set lineColor = 2

set baseDir = "data"
set variable = "rh"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

foreach level (850 700)

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}

 gdplot2_gf << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${inFile}"
  GDATTIM  = "f${TIME}"
  GLEVEL   = "${level}"
  GVCORD = PRES
  PANEL  = 0                                                                       
  SKIP   = 0
  SCALE  = 0
  GDPFUN = relh
  TYPE   = c/f
  CONTUR  =1                                                                       
  CINT   = 10;20;80;90
  LINE   = 32//2
  FINT    =10;30;70;90
  FLINE  = 18;8;0;22;23
  HILO   = 0
  HLSYM  = 0
  CLRBAR   = 
  WIND   = 
  REFVEC  =                                                                        
  TITLE  = 
  TEXT   =                                                             
  CLEAR  = yes                                                                     
  DEVICE  =xw                                                                      
  STNPLT  =                                                                        
  SATFIL  =                                                                        
  RADFIL  =                                                                        
  STREAM  =                                                                        
  POSN    =4                                                                       
  COLORS = 2                                                                       
  MARKER = 2                                                                       
  GRDLBL = 5    
  GAREA = 19.00;-119.00;50.00;-56.00
  PROJ = STR/90;-100;0
  MAP      = 0                                                                
  LUTFIL  =none
  FILTER  =yes
  DEVICE = "gif|init_${model}_${level}_${variable}_f${TIME}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts
 # convert to a transparent image layer.
 convert init_${model}_${level}_${variable}_f${TIME}.gif -transparent black ${imgDir}/f${TIME}.gif
 rm init_${model}_${level}_${variable}_f${TIME}.gif

 end

end