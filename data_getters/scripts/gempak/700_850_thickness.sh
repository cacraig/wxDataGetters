#!/bin/csh

# Usage ./avor.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 4 paremeters must be defined!"
    echo "Usage ./700_850_thickness.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 

set variable = "700_850_thickness"
set level = "700"

set gdFile = ${model}".gem"

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set baseDir = "data"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4

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

  foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC")
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

    set proj = "MER//NM"

    set regionName = ${REGION}

    if (${REGION} == "19.00;-119.00;50.00;-56.00") then
      set proj = "STR/90;-100;0"
      set regionName = "CONUS"
    endif


gdplot2_gf << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${gdFile}"
  GDATTIM  = "f${TIME}"
  GLEVEL = 700:850
  GVCORD = pres
  PANEL  = 0                                                                       
  SKIP   = 0
  SCALE  = 0
  GDPFUN = (sub(hght@700,hght@850)) ! (sub(hght@700,hght@850)) ! (sub(hght@700,hght@850))
  TYPE   = c
  CONTUR = 1
  CINT   = 10/1000/1530 ! 1540;1550 ! 10/1560/2500
  LINE   = 24/1/1/2 ! 27;26/1/1/2 ! 23/1/1/2
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
