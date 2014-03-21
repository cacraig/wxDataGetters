#!/bin/csh

# Usage ./avor.sh  <model>  <time1,time2,...>  <inFile>


echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./avor.sh  <model>  <time1,time2,...>  <inFile> <MODEL path>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set inFile = $3 

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

#Set output Directory = Timestamp_model
set outDir = data/${timeStamp}_${model}

set MODEL_PATH  = $4 

set variable = "wind"

# Make our run directory.
if !(-e ${outDir}) then
  echo "Making Dir..."
  mkdir ${outDir}
endif

foreach TIME ($times:q)

foreach level (500 850)
 gdplot << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${inFile}"
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
  HILO   =                                                                        
  HLSYM  =                                                                        
  REFVEC =       
  TITLE =                                                                       
  CLEAR =  "yes"    
  GAREA    = "us" 
  IJSKIP   = "0"
  PROJ     = 
  MAP      = "0"
  STNPLT   =
  DEVICE = "gif|${model}_${variable}_${level}mb_init_f${TIME}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts
 # convert to a transparent image layer.
 convert ${model}_${variable}_${level}mb_init_f${TIME}.gif -transparent white ${outDir}/${model}_${variable}_${level}mb_f${TIME}.gif
 rm ${model}_${variable}_${level}mb_init_f${TIME}.gif

 end

end
