#!/bin/csh

# Usage ./avor.sh  <model>  <time1,time2,...>  <inFile>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./avor.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 

set variable = "avor"

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

set baseDir = "data"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 
set gdFile = ${model}".gem"
set proj = "MER"

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

  if (${model} == 'gfs' && ${TIME} > 192) then
    set gdFile = ${runTime}"_2p5.gem"
  endif

  if (${model} == 'gfs' && ${TIME} < 192 && ${TIME} > 120) then
    set gdFile = ${runTime}"_p5_2.gem"
  endif

  if (${model} == 'gfs' && ${TIME} < 192 && ${TIME} <= 120) then
    set gdFile = ${runTime}"_p5.gem"
  endif

  if (${model} == 'nam' && ${TIME} > 60) then
    set gdFile = ${runTime}"_3.gem"
  endif

  if (${model} == 'nam' && ${TIME} <= 60 && ${TIME} > 30) then
    set gdFile = ${runTime}"_2.gem"
  endif

  if (${model} == 'nam' && ${TIME} <= 30) then
    set gdFile = ${runTime}"_1.gem"
  endif

foreach level (250 500 850)

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}

  foreach REGION ("WA" "19.00;-119.00;50.00;-56.00" "NC")
    set regionName = ${REGION}
    set proj = "MER"

    if (${REGION} == "19.00;-119.00;50.00;-56.00") then
      set proj = "STR/90;-100;0"
      set regionName = "CONUS"
    endif


 gdplot_gf << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${gdFile}"
  GDATTIM  = "f${TIME}"
  CLEAR    = "n"
  GLEVEL   = "${level}"
  GVCORD   = "PRES"
  PANEL    = "0"
  GFUNC    =  "abs(avor(wnd))"
  HILO     =  
  HLSYM    =  
  CLEAR  = yes
  PANEL  = 0
  SCALE  = 5
  GVECT= 
  CLRBAR = 
  CONTUR = 1
  SKIP  =  0
  TITLE = 
  FINT   = 16;20;24;28;32;36;40;44
  FLINE  = 0;23-15
  CTYPE  = c/f
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
