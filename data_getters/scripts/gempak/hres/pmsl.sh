#!/bin/csh

# Usage ./pmsl.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 4 paremeters must be defined!"
    echo "Usage ./pmsl.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 

set variable = "pmsl"

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set baseDir = "data"
set lineColor = 13
set gdFile = ${model}".gem"
#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4

set proj = "MER//NM"


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

 set gdFile = ${runTime}"f"${TIME}".gem"
  
  
 # Reset line color!
 set lineColor = 13
 set imgDir = ${baseDir}/${model}/${timeStamp}/sfc/${variable}
 echo imgDir
 mkdir -p ${baseDir}/${model}/${timeStamp}/sfc/${variable}


 if (${model} == "nam4km") then
   @ lineColor = $lineColor + 5
 endif


  foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC" "OK")
    set regionName = ${REGION}
    set proj = "STR/90;-100;0"

    if (${REGION} == "19.00;-119.00;50.00;-56.00") then
      set proj = "STR/90;-100;0"
      set regionName = "CONUS"
    endif

    if (${REGION} == "NC") then
      set proj = "lea/35.50;-79.25;0/NM"
      set regionName = "NC"
    endif

    if (${REGION} == "OK") then
      set proj = "lea/35.75;-97.25;0/NM"
      set regionName = "OK"
    endif

    if (${REGION} == "WA") then
      set proj = "lea/47.25;-120.00;0/NM"
      set regionName = "WA"
    endif

gdplot2_gf << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${gdFile}"
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
  GAREA  = ${REGION}
  PROJ   = ${proj}    
  MAP      = "0"
  MSCALE   = "0"
  LATLON   = 
  STNPLT   =  
  DEVICE   = "gif|init_${model}_sfc_${variable}_f${TIME}.gif|1280;1024| C"
  run
 exit
EOF
   # clean output buffer/gifs, and cleanup
   gpend
   rm last.nts
   rm gemglb.nts
   # convert to a transparent image layer.
   convert init_${model}_sfc_${variable}_f${TIME}.gif -transparent black ${imgDir}/${regionName}_f${TIME}.gif
   rm init_${model}_sfc_${variable}_f${TIME}.gif
 end

end
