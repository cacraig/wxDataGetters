#!/bin/csh

# Usage ./wind.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>


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

set baseDir = "data"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 
set gdFile = ${model}".gem"
set proj = "MER//NM"

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

#Default barb/color width
set barbColor = 31

set variable = "barbs"


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

 if (${model} == "ecmf1") then
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

  foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC" "OK" "CA" "CHIFA" "CENTUS" "MA" "18.00;-92.00;54.00;-40.00" "WSIG" "TATL")
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
  GAREA  = ${REGION}
  PROJ   = ${proj}    
  GDPFUN   = wnd 
  CLEAR    = n
  GLEVEL   = 500
  GVCORD   = PRES
  PANEL    = 0
  SKIP     =  1/2  
  IJSKIP   = 30
  GLEVEL   = "${level}"
  GVCORD   = pres 
  TYPE     = b 
  CINT     = 0/32/32
  FINT     = 15;20;30;35;40;45;50;55;60;65;70;75;80
  FLINE    = 32;30-19
  CLRBAR   = 31 
  PANEL    = 0
  SKIP     = 0                 
  SCALE    = 0                
  CONTUR   = 0      
  MAP      = 0            
  HILO     =   
  LATLON   = 
  STNPLT   =  
  SATFIL   =  
  RADFIL   = 
  LUTFIL   =  
  STREAM   =  
  POSN     = 4
  COLORS   = 2
  MARKER   = 2
  GRDLBL   = 5
  FILTER   = YES 
  LINE     = 4/1/5
  HLSYM    = 1/3/23//HW 
  WIND     = ${barbColor}/.6/2
  TXTCOL   = 
  TXTYPE   = 
  TXTFIL   =  
  INFO     =  
  LOCI     =  
  ANOTLN   =  
  ANOTYP   = 
  IJSKIP   = 
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
