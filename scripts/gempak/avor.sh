#!/bin/csh

# Usage ./avor.sh  <model>  <time1,time2,...>  <inFile>

# Initialize ENV vars.
.  /home/cacraig/gempak/GEMPAK7/Gemenviron.profile

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./avor.sh  <model>  <time1,time2,...>  <inFile>"
    exit( 1 )
endif


set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set inFile = $3 

set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}

#Set output Directory = Timestamp_model
set outDir = ${timeStamp}_${model}

# Make our run directory.
if !(-e ${outDir}) then
  echo "Making Dir..."
  mkdir ${outDir}
endif

foreach TIME ($times:q)

foreach level (500 850)
 gdplot << EOF 
         
  GDFILE   = "$MODEL/${model}/${inFile}"
  GDATTIM  = "f${TIME}"
  CLEAR    = "n"
  GLEVEL   = "${level}"
  GVCORD   = "PRES"
  PANEL    = "0"
  SKIP     =  
  SCALE    = "5"
  GFUNC   = "avor(WND)"
  CTYPE    = "f"
  CONTUR   = "2"
  CINT     = "2"
  LINE     = "1/1"
  !FINT     = "10;12;14;16;18;20;22;24"
  !FLINE    = "101;21;22;23;5;19;17;16;15;5"
  fint="-15;-12;-9;-6;-3;3;6;9;12;15" 
  fline="7;30;24;4;26;31;22;20;17;16;15"
  HILO     =  
  HLSYM    =  
  CLRBAR   = "31/V/LL/"
  GVECT    =  
  WIND     = "0"
  REFVEC   =  
  TITLE    = "31/-2/GFS ~"
  TEXT     = "1/2//hw"
  GAREA    = "us"  
  IJSKIP   = "0"
  PROJ     = "str/90;-100;0"
  MAP      = "0"
  !BORDER   = "0/1/1"
  !BND = "0"
  MSCALE   = "0"
  LATLON   = "0"
  STNPLT   =  
  DEVICE = "gif|${model}_avor_${level}mb_init_f${TIME}.gif|1280;1024| C"
  run
 exit
EOF
 # clean output buffer/gifs, and cleanup
 gpend
 rm last.nts
 rm gemglb.nts
 # convert to a transparent image layer.
 convert ${model}_avor_${level}mb_init_f${TIME}.gif -transparent white ${outDir}/${model}_avor_${level}mb_f${TIME}.gif
 rm ${model}_avor_${level}mb_init_f${TIME}.gif

 end

end
