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

set baseDir = "data"
set variable = "avor"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
endif

if (${model} == 'nam12km') then
  set extension = "_nam218.gem"
endif

foreach TIME ($times:q)

foreach level (250 500 850)

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 
 set shortTime = ${TIME}

 if (${model} == "nam12km") then
   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 endif 

 gdplot << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${runTime}f${TIME}${extension}"
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
  GAREA = "19.00;-119.00;50.00;-56.00"
  PROJ = "STR/90;-100;0"
  MAP      = "0"
  MSCALE   = "0"
  LATLON   = 
  STNPLT   =  
  DEVICE = "gif|init_${model}_${level}_${variable}_f${shortTime}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts

 # convert to a transparent image layer.
 convert init_${model}_${level}_${variable}_f${shortTime}.gif -transparent black ${imgDir}/f${shortTime}.gif
 rm init_${model}_${level}_${variable}_f${shortTime}.gif

 end

end