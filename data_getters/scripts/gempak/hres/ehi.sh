#!/bin/csh

# Usage ./ehi.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>


echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./ehi.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
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

set variable = "EHI"


foreach TIME ($times:q)

  set gdFile = ${runTime}"f"${TIME}".gem"
  

foreach level (1000 3000)
 set variable = 0_${level}_"EHI"
 set imgDir = ${baseDir}/${model}/${timeStamp}/comp/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/comp/${variable}

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
  GAREA  = ${REGION}
  PROJ   = ${proj} 
  map      = 0
  clear    = y
  GDPFUN   = quo(mul(cape@0%none,hlcy),160000)
  GLEVEL   = ${level}:0
  GVCORD   = hght
  TYPE     = f
  CINT     = 
  FINT     = 0;1;2;3;4;5;6;7;8;9;10
  FLINE    = 32;32;10;12;14;16;18;20;22;24;26;28
  CLRBAR   = 1/V/LR/.97;.45/
  PANEL    = 0
  SKIP     = 0
  SCALE    = 0                 
  CONTUR   = 2                   
  HILO     = 0
  LATLON   = 
  STNPLT   =  
  SATFIL   =  
  RADFIL   = 
  LUTFIL   =  
  STREAM   =  
  POSN     = 2
  COLORS   = 2
  MARKER   = 0
  GRDLBL   = 0
  FILTER   = 0
  LINE     = 32/1/1!4/1/1
  HLSYM    = 0
  WIND     = 0
  INFO     =  
  LOCI     =  
  ANOTLN   =  
  ANOTYP   =  
  TITLE    = 
  DEVICE = "gif|init_${model}_0_${level}_${variable}_f${TIME}.gif|1280;1024| C"
  run   
 exit
EOF
     # clean output buffer/gifs, and cleanup
     gpend
     rm last.nts
     rm gemglb.nts
     # convert to a transparent image layer.
     convert init_${model}_0_${level}_${variable}_f${TIME}.gif -transparent black ${imgDir}/${regionName}_f${TIME}.gif
     rm init_${model}_0_${level}_${variable}_f${TIME}.gif

    end

 end

end
