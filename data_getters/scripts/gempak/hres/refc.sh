echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./refc.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
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
set variable = "refc"

#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -r ${baseDir}/${model}/${timeStamp}
endif

if (${model} == 'nam12km') then
  set extension = "_nam218.gem"
endif

if (${model} == 'nam4km') then
  set extension = "_nam4km.gem"
endif

foreach TIME ($times:q)

 set imgDir = ${baseDir}/${model}/${timeStamp}/comp/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/comp/${variable}
 
 set shortTime = ${TIME}

 if (${model} == "nam12km") then
   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 endif 

 if (${model} == "nam4km") then
   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 endif 

 gdplot3_gf << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${runTime}f${TIME}${extension}"
  GDATTIM  = "f${TIME}"
  GLEVEL = 0
  GVCORD = NONE
  PANEL  = 0                                                                       
  SKIP   = 0
  SCALE  = 0
  GDPFUN = REFC
  TYPE   = f
  CONTUR = 0                                         
  HILO   =                                                                          
  HLSYM  =      
  FINT   = 5;10;15;20;25;30;35;40;45;50;55;60;65;70;75;80
  FLINE  = 0;26;24;4;21;22;23;20;18;17;15;14;28;29;7;31                                   
  WIND   = 
  REFVEC =                                                                                                                                   
  CLEAR  = yes                                                                     
  STNPLT =                                                                         
  SATFIL =                                                                         
  RADFIL = 
  TITLE  =                                                                        
  STREAM =        
  GAREA  = 19.00;-119.00;50.00;-56.00
  PROJ   = STR/90;-100;0                                                                 
  POSN   =                                                                         
  COLORS = 1 
  MAP    = 1                                                                      
  MARKER =                                                                        
  GRDLBL =   
  CLRBAR = 1                                                                     
  LUTFIL = none
  FILTER = yes
  DEVICE = "gif|${imgDir}/f${shortTime}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts

end