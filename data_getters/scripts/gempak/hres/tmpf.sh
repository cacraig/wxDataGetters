echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./hght.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
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
set variable = "tmpf"

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

 set imgDir = ${baseDir}/${model}/${timeStamp}/sfc/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/sfc/${variable}
 
 set shortTime = ${TIME}

 if (${model} == "nam12km") then
   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 endif 

 gdplot2 << EOF 
         
  GDFILE   = "${MODEL_PATH}/${model}/${runTime}f${TIME}${extension}"
  GDATTIM  = "f${TIME}"
  GLEVEL = 2
  GVCORD = HGHT
  PANEL  = 0                                                                       
  SKIP   = 0
  SCALE  = 0
  GDPFUN = ADD( MUL( SUB( TMPK , 273.15 ), QUO( 9 , 5 ) ) , 32 )
  TYPE   = f
  CONTUR = 0                                                                      
  CINT   = -20;-10;0;10;20;30;40;50;60;70;80;90;100;110
  LINE   = 32/1/2/2
  FINT   = -20;-10;0;10;20;30;40;50;60;70;80;90;100;110
  FLINE  = 30;29;28;27;26;25;24;23;20;17;16;15;14;7
  HILO   =                                                                          
  HLSYM  =                                                                        
  WIND   = 18/1/1
  REFVEC =                                                                                                                                   
  CLEAR  = yes                                                                     
  STNPLT =                                                                         
  SATFIL =                                                                         
  RADFIL = 
  TITLE  =                                                                        
  STREAM =        
  GAREA  = 19.00;-119.00;50.00;-56.00
  PROJ   = STR/90;-100;0                                                                 
  POSN   =  4                                                                       
  COLORS = 2 
  MAP    = 0                                                                      
  MARKER = 2                                                                       
  GRDLBL = 5                                                                       
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