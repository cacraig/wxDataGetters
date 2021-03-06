#!/bin/csh

# Usage ./tmpf_txt.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./tmpf_txt.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 

set variable = "tmpf_txt"

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set baseDir = "data"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 
set gdFile = ${model}".gem"
set proj = "MER//NM"
set level = "sfc"
set ijskip = "25"

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

  set gdFile = ${runTime}"f"${TIME}".gem"
  set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
  mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}



  foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC" "OK" "CA" "CHIFA" "CENTUS" "MA" "18.00;-92.00;54.00;-40.00")
    set regionName = ${REGION}
    set proj = "STR/90;-100;0"

    if (${REGION} == "19.00;-119.00;50.00;-56.00") then
      set proj = "STR/90;-100;0"
      set regionName = "CONUS"
      set ijskip = "35"
    endif

    if (${REGION} == "NC") then
      set proj = "lea/35.50;-79.25;0/NM"
      set regionName = "NC"
      set ijskip = "25"
    endif

    if (${REGION} == "OK") then
      set proj = "lea/35.75;-97.25;0/NM"
      set regionName = "OK"
      set ijskip = "25"
    endif

    if (${REGION} == "WA") then
      set proj = "lea/47.25;-120.00;0/NM"
      set regionName = "WA"
      set ijskip = "25"
    endif

    if (${REGION} == "CA") then
      set proj = "lea/37.00;-119.75;0/NM"
      set regionName = "CA"
      set ijskip = "25"
    endif

    if (${REGION} == "CHIFA") then
      set proj = "lea/42.00;-93.00;0/NM"
      set regionName = "CHIFA"
      set ijskip = "30"
    endif

    if (${REGION} == "CENTUS") then
      set proj = "LCC/36.15;-91.20;36.15/NM"
      set regionName = "CENTUS"
      set ijskip = "30"
    endif

    if (${REGION} == "MA") then
      set proj = "lea/42.25;-72.25;0/NM"
      set regionName = "NEUS"
      set ijskip = "25"
    endif

    if (${REGION} == "18.00;-92.00;54.00;-40.00") then
      set proj = "LCC/30;-85;30/NM"
      set regionName = "EASTUS"
      set ijskip = "35"
    endif

    # if (${REGION} == "WSIG") then
    #   set proj = "MER//NM"
    #   set regionName = "EPAC"
    #   set ijskip = "35"
    # endif

    # if (${REGION} == "TATL") then
    #   set proj = "MER//NM"
    #   set regionName = "TATL"
    #   set ijskip = "35"
    # endif

gdmap_gf << EOFD

 GLEVEL   = 2
 GVCORD   = hght
 GFUNC    = sm9s(ADD( MUL( SUB( TMPK , 273.15 ), QUO( 9 , 5 ) ) , 32 ))
 GDFILE   = "${MODEL_PATH}/${model}/${gdFile}"
 GDATTIM  = "f${TIME}"
 GAREA  = ${REGION}
 PROJ   = ${proj}  
 IJSKIP   = ${ijskip}
 COLORS   = 31
 TITLE    = 
 SCALE    = 
 DEVICE   = "gif|init_${model}_${level}_${variable}_f${TIME}.gif|1280;1024| C"
 CLEAR    = y
 TEXT     = 1.1//1.8/
 GRDLBL   = 0
 MAP = 0
run

EOFD
   # clean output buffer/gifs, and cleanup
   gpend
   rm last.nts
   rm gemglb.nts
   # convert to a transparent image layer.
   convert init_${model}_${level}_${variable}_f${TIME}.gif -transparent black ${imgDir}/${regionName}_f${TIME}.gif
   rm init_${model}_${level}_${variable}_f${TIME}.gif
  end
end