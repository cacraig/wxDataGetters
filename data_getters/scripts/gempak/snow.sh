#!/bin/csh

# http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table4-2.shtml
# SWEM

# Usage ./snow.sh  <model>  <time1,time2,...>  <inFile> <MODEL path> <previousTime>


echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "" || $5 == "") then
    echo "All 5 paremeters must be defined!"
    echo "Usage ./snow.sh  <model>  <time1,time2,...>  <runTime> <MODEL path> <previousTime>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 
set runHour = `echo $3 | tail -c 3`



set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set YMD = `echo ${timeStamp} |sed 's/.\{2\}$//'`
set MODEL_PATH  = $4 

set variable = "snow"

set baseDir = "data"
set gdFile = ${model}".gem"
#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 
set proj = "MER"

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

set previous = $5

foreach TIME ($times:q)

  set gdFile = ${runTime}"f"${TIME}".gem"


  foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC")
    set regionName = ${REGION}
    set proj = "MER"
    
    if (${REGION} == "19.00;-119.00;50.00;-56.00") then
      set proj = "STR/90;-100;0"
      set regionName = "CONUS"
    endif

   set imgDir = ${baseDir}/${model}/${timeStamp}/sfc/${variable}
   mkdir -p ${baseDir}/${model}/${timeStamp}/sfc/${variable}

gdplot2_gf << EOF 
       
  GDFILE  = "${MODEL_PATH}/${model}/${gdFile}"
  GDATTIM = f${previous}:f${TIME}
  GLEVEL  = 0 
  GVCORD  = none
  PANEL   = 0 
  SKIP    = 
  GAREA   = 19.00;-119.00;50.00;-56.00
  SCALE   = 0
  clear   = y
  TYPE    = f     
  CLRBAR  = 31 
  POSN     = 4
  COLORS   = 2
  MARKER   = 2
  GRDLBL   = 5         
  CINT    = 
  FINT    = 0.5;1;2;3;4;5;6;7;8;9;10;11;12;13; ! 0.5;1;2;3;4;5;6;7;8;9;10;11;12;13;
  FLINE   = 0;21-30;14-20;5;6;7;8;9;10;11;12;13 ! 0;21-30;14-20;5;6;7;8;9;10;11;12;13
  GDPFUN  = MUL(quo(swemdiff,25.4),tminrat^f${TIME}) ! MUL(quo(swemdiff,25.4),tmaxrat^f${TIME}) 
  CTYPE   = 
  GAREA   = ${REGION}
  PROJ    = ${proj}    
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
   convert init_${model}_sfc_${variable}_f${TIME}.gif -transparent black ${imgDir}/${regionName}_f${TIME}.gif
   rm init_${model}_sfc_${variable}_f${TIME}.gif
  end

  set previous = ${TIME}


end