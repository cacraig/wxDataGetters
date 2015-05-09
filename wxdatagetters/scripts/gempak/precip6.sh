#!/bin/csh

# Usage ./precip6.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>


echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./precip6.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 



set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set MODEL_PATH  = $4 

set variable = "precip6"
set gdFile = ${model}".gem"
set baseDir = "data"

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


 foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC" "OK" "CA" "CHIFA" "CENTUS" "MA" "18.00;-92.00;54.00;-40.00")
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
      set proj = "LCC/36.15;-91.20;36.15/NM"
      set regionName = "CENTUS"
    endif

    if (${REGION} == "MA") then
      set proj = "lea/42.25;-72.25;0/NM"
      set regionName = "NEUS"
    endif

    if (${REGION} == "18.00;-92.00;54.00;-40.00") then
      set proj = "LCC/30;-85;30/NM"
      set regionName = "EASTUS"
    endif

   set imgDir = ${baseDir}/${model}/${timeStamp}/sfc/${variable}
   mkdir -p ${baseDir}/${model}/${timeStamp}/sfc/${variable}

gdplot2_gf << EOF 
       
  GDFILE  = "${MODEL_PATH}/${model}/${gdFile}"
  GDATTIM = "f${TIME}"
  GLEVEL  = 0 
  GVCORD  = none 
  PANEL   = 0 
  SKIP    = 
  SCALE   = 0 
  GDPFUN   = p06i 
  CTYPE   = f
  CONTUR  = 1 
  CINT    = 0.25;0.5;0.75;1;1.5;2.0;3.0
  TYPE    = f
  LINE    = 16/10/1/1 
  FINT    = 0.01;0.1;0.25;0.5;0.75;1;1.5;2.0;3.0
  FLINE   = 0;21;22;23;20;17;15;2;7 
  HILO    = 
  HLSYM   = 
  GVECT   = 
  WIND    = bm32/0.8 
  REFVEC  = 
  CLRBAR  = 1/H/LR/.75;.05/
  GAREA  = ${REGION}
  PROJ   = ${proj}    
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


end