#!/bin/csh

# Usage ./isotachs.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>


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

set MODEL_PATH  = $4 

set variable = "isotachs"

set baseDir = "data"
set gdFile = ${model}".gem"
#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4


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
    set gdFile = ${runTime}"_4.gem"
  endif

  if (${model} == 'nam' && ${TIME} <= 60 && ${TIME} > 39) then
    set gdFile = ${runTime}"_3.gem"
  endif

  if (${model} == 'nam' && ${TIME} <= 39 && ${TIME} > 18) then
    set gdFile = ${runTime}"_2.gem"
  endif

  if (${model} == 'nam' && ${TIME} <= 18) then
    set gdFile = ${runTime}"_1.gem"
  endif

foreach level (250 500 850)

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 #cd ${baseDir}/${model}/${timeStamp}/${level}/${variable}

 gdplot_gf << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${gdFile}"
  GDATTIM  = "f${TIME}"
  CLEAR    = "n"
  GLEVEL   = "${level}"
  GVCORD   = "PRES"
  PANEL    = "0"
  SKIP  =  "1/2"   
  SCALE =  "0"                                                               
  GFUNC =  "knts((mag(wnd)))"                                               
  CTYPE =  "c/f"                                                                  
  CONTUR = "1"                                                                    
  CINT   = "30;50;70;90;110;130;150"                                      
  LINE   = "27/5/2/1"                                                    
  FINT   = "70;90;110;130;150"                                                  
  FLINE  = "0;25;24;29;7;15"
  WIND   =    
  GVECT  = 
  HILO   =                                                                        
  HLSYM  =                                                                        
  REFVEC =       
  TITLE =                                                                       
  CLEAR =  "yes"    
  IJSKIP   = "0"
  GAREA = "19.00;-119.00;50.00;-56.00"
  PROJ = "STR/90;-100;0"
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
 convert init_${model}_${level}_${variable}_f${TIME}.gif -transparent black ${imgDir}/f${TIME}.gif
 rm init_${model}_${level}_${variable}_f${TIME}.gif

 end

end
