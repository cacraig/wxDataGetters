#!/bin/csh

# Usage ./avor.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 4 paremeters must be defined!"
    echo "Usage ./850_1000_thickness.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 

set variable = "850_1000_thickness"
set level = "850"

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set baseDir = "data"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 

set gdFile = ${model}".gem"
set proj = "MER//NM"

if ${model} == "nam" then
    set gdFile = ${runTime}".gem"
  endif

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

  set gdFile = ${runTime}"f"${TIME}".gem"

  foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC" "OK")

   # Reset line color!
   set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
   mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}

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
  GLEVEL = 850:1000
  GVCORD = pres
  PANEL  = 0                                                                       
  SKIP   = 0
  SCALE  = 0
  GDPFUN = (sub(hght@850,hght@1000)) ! (sub(hght@850,hght@1000)) ! (sub(hght@850,hght@1000))
  TYPE   = c
  CONTUR = 1
  CINT   = 10/1000/1280 ! 1290;1300;1310;1320 !10/1330/1800
  LINE   = 24/1/1/2 ! 27;26;25;25/1/1/2 ! 23/1/1/2
  FINT   = 
  FLINE  = 
  HILO   = 
  HLSYM  = 
  CLRBAR =
  WIND   =
  REFVEC =                                                                         
  TITLE  = 
  TEXT   =                                                              
  CLEAR  = yes                                                                     
  STNPLT =                                                                         
  SATFIL =                                                                         
  RADFIL =     
  GAREA  = ${REGION}
  PROJ   = ${proj}                                                                           
  STREAM =   
  MAP    = 0                                                                      
  POSN   = 4                                                                       
  COLORS = 2                                                                       
  MARKER =  2                                                                       
  GRDLBL =  5                                                                       
  LUTFIL =  none
  FILTER = yes
  DEVICE   = "gif|init_${model}_${level}_${variable}_f${TIME}.gif|1280;1024| C"
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
