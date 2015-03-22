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
set proj = "MER//NM" 


# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

if (${model} == 'nam12km') then
  set extension = ".gem"
endif

if (${model} == 'nam4km') then
  set extension = ".gem"
endif

foreach TIME ($times:q)

 set gdFile = ${runTime}"f"${TIME}".gem"

 set imgDir = ${baseDir}/${model}/${timeStamp}/comp/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/comp/${variable}
 
 set shortTime = ${TIME}


gddiag << EOFD
glevel = 2
garea = 
gvcord = hght
gdattim = "f${TIME}"
gdfile = "${MODEL_PATH}/${model}/${gdFile}"
gdoutf = "${MODEL_PATH}/${model}/${gdFile}"
gpack = none
!
gfunc = sgt(tmpk,272)
GRDNAM = rain1@0%none
r

gfunc = sgt(tmpk@30:0%pdly,272)
grdnam = rain2@0%none
r

glevel = 0
gvcord = none
gfunc = mask(rain1,rain2)
grdnam = rain@0%none
r

glevel = 2
gvcord = hght
gfunc = sle(tmpk,276)
grdnam = snow1@0%none
r

gfunc = sle(tmpk@30:0%pdly,273)
grdnam = snow2@0%none
r

glevel = 0
gvcord = none
gfunc = mask(snow1,snow2)
grdnam = snow
r

glevel = 2
gvcord = hght
gfunc = sle(tmpk,273.1)
grdnam = frzn1@0%none
r

gfunc = mask(frzn1@0%none,rain2@0%none)
grdnam = frzn@0%none
r

e
EOFD

 # if (${model} == "nam12km") then
 #   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 # endif 

 # if (${model} == "nam4km") then
 #   set shortTime = `echo ${TIME} | awk '{print substr($0,2,3)}'`
 # endif 

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


gdcntr_gf << EOF
  device   = "gif|${imgDir}/${regionName}_f${shortTime}.gif|1280;1024| C"
  gdfile   = "${MODEL_PATH}/${model}/${gdFile}"
  map      = 0
  clear    = y
  gdattim  = "f${TIME}"
  text     = 
  TITLE    = 
  GLEVEL   = 0
  GVCORD   = none
  CTYPE    = F
  PANEL    = 0
  SKIP     = 0
  SCALE    = 0
  CONTUR   = 0
  HILO     =
  LATLON   = 0
  STNPLT   =
  SATFIL   =
  RADFIL   =
  LUTFIL   =
  STREAM   =

  GAREA  = ${REGION}
  PROJ   = ${proj} 
   
  POSN     = 0
  COLORS   = 1
  MARKER   = 0
  GRDLBL   = 0
  FILTER   = YES

  GFUNC    = mask(refc,rain^f${TIME})
  FINT   = 5;10;15;20;25;30;35;40;45;50;55;60;65;70;75;80
  FLINE  =  0;0;0;21;3;22;23;20;18;17;15;14;28;29;7
  CLRBAR   = 1/V/LL/0.001;0.1/0.5;0.01/1|.7/1/1
  r

  GFUNC    = mask(refc,frzn^f${TIME})
  FINT   =  5;10;15;20;25;30;35;40
  FLINE  =  0;11;11;12;13;14;15;16;16
  CLRBAR   = 1/V/LL/0.025;0.1/0.5;0.01/1|.7/1/1
  clear = n
  title =
  r

  GFUNC = mask(refc,snow^f${TIME})
  FINT   = 5;10;15;20;25;30;35;40
  FLINE  =  0;6;6;27;26;25;24;4;4
  CLRBAR   = 1/V/LL/0.050;0.1/0.5;0.01/1|.7/1/1
  r

  exit
EOF
   # clean output buffer/gifs, and cleanup
   gpend

   rm last.nts
   rm gemglb.nts
   convert ${imgDir}/${regionName}_f${shortTime}.gif -transparent black ${imgDir}/${regionName}_f${shortTime}.gif
  end

end
