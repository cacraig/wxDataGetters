#!/bin/csh

# Usage ./hght.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./avor.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set lineColor = 2
set gdFile = ${model}".gem"
set baseDir = "data"
set variable = "hght"
set proj = "MER//NM"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)
  
  set gdFile = ${runTime}"f"${TIME}".gem"

  # if (${model} == 'gfs' && ${TIME} > 192) then
  #   set gdFile = ${runTime}"_2p5.gem"
  # endif

  # if (${model} == 'gfs' && ${TIME} < 192 && ${TIME} > 120) then
  #   set gdFile = ${runTime}"_p5_2.gem"
  # endif

  # if (${model} == 'gfs' && ${TIME} < 192 && ${TIME} <= 120) then
  #   set gdFile = ${runTime}"_p5.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} > 60) then
  #   set gdFile = ${runTime}"_4.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} <= 60 && ${TIME} > 39) then
  #   set gdFile = ${runTime}"_3.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} <= 39 && ${TIME} > 18) then
  #   set gdFile = ${runTime}"_2.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} <= 18) then
  #   set gdFile = ${runTime}"_1.gem"
  # endif

foreach level (250 500 850)

 if (${level} == 250) then
   set lineColor = 28
 endif

 if (${level} == 500) then
   set lineColor = 21
 endif

 if (${level} == 850) then
   set lineColor = 17
 endif

 if (${level} == 1000) then
   set lineColor = 13
 endif

 if (${model} == "ecmf1") then
  @ lineColor = $lineColor
 endif

 if (${model} == "nam") then
   echo "True"
   @ lineColor = $lineColor + 1
 endif


 if (${model} == "gfs") then
  echo "GFS"
  @ lineColor = $lineColor + 2
 endif

 if (${model} == "ruc") then
  @ lineColor = $lineColor + 3
 endif

 if (${model} == "ukmet") then
  @ lineColor = $lineColor + 3
 endif

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}

 foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC" "OK" "WSIG" "TATL" "CA" "CHIFA" "CENTUS" "MA" "WWE")

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

    if (${REGION} == "CA") then
      set proj = "lea/37.00;-119.75;0/NM"
      set regionName = "CA"
    endif

    if (${REGION} == "CHIFA") then
      set proj = "lea/42.00;-93.00;0/NM"
      set regionName = "CHIFA"
    endif

    if (${REGION} == "CENTUS") then
      set proj = "lea/36.15;-91.20;0/NM"
      set regionName = "CENTUS"
    endif

    if (${REGION} == "MA") then
      set proj = "lea/42.25;-72.25;0/NM"
      set regionName = "NEUS"
    endif

    if (${REGION} == "WWE") then
      set proj = "lea/36.00;-78.00;0/NM"
      set regionName = "EASTUS"
    endif

    if (${REGION} == "WSIG") then
      set proj = "MER//NM"
      set regionName = "EPAC"
    endif

    if (${REGION} == "TATL") then
      set proj = "MER//NM"
      set regionName = "TATL"
    endif


gdplot2_gf << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${gdFile}"
  GDATTIM  = "f${TIME}"
  CLEAR    = "n"
  GLEVEL   = "${level}"
  GVCORD   = "PRES"
  PANEL    = "0"
  SKIP     =  
  SCALE    = "-1"
  GDPFUN    = "hght"
  CTYPE    = "c"
  CONTUR   = 
  CINT     = "8"
  LINE     = "${lineColor}/1/2/1"
  HILO     =  
  HLSYM    =  
  CLRBAR   = 
  GVECT    =  
  WIND     = 
  REFVEC   =  
  TITLE    = 
  TEXT     = "1/21//hw"
  IJSKIP   = "0"
  GAREA  = ${REGION}
  PROJ   = ${proj}    
  MAP      = "0"
  STNPLT   =
  DEVICE = "gif|init_${model}_${level}_${variable}_f${TIME}.gif|1280;1024| C"
  run
 exit
EOF
   # clean output buffer/gifs, and cleanup
   gpend
   rm last.nts
   rm gemglb.nts
   # convert to a transparent image layer.
   convert init_${model}_${level}_${variable}_f${TIME}.gif -transparent black ${imgDir}/${regionName}_f${TIME}.gif
   rm init_${model}_${level}_${variable}_f${TIME}.gif
  end

 end

end
