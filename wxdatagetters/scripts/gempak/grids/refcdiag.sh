echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./refcdiag.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
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

end