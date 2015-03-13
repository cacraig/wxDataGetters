echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "" || $5 == "") then
    echo "All 5 paremeters must be defined!"
    echo "Usage ./snowratiodiag.sh  <model>  <time1,time2,...>  <runTime> <MODEL path> <previousTime>"
    exit( 1 )
endif

set model  = $1
set times  = `echo $2:q | sed 's/,/ /g'`
set runTime = $3 
set runHour = `echo $3 | tail -c 3`



set timeStamp = `echo $3 | sed 's/_/ /g'`
# Get run timeStamp YYYYMMDDHH
set timeStamp = ${timeStamp[1]}
set YMD = `echo ${timeStamp} |sed 's/.\{2\}$//'`

set MODEL_PATH  = $4 

set variable = "snow"

set baseDir = "data"
set gdFile = ${model}".gem"
#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 
set proj = "MER"

set previous = $5

foreach TIME ($times:q)

set gdFile = ${runTime}"f"${TIME}".gem"
set previousgdFile = ${runTime}"f"${previous}".gem"

# echo "${TIME}"
# echo "${MODEL_PATH}/${model}/${gdFile}"
# echo "${previous}"
# echo "SUB(swem2^F${TIME}, swem1^F${previous})"
# echo "${MODEL_PATH}/${model}/${previousgdFile}"
# echo ""

gddiag << EOFD
garea = 
gvcord = pres
gdattim = F${TIME}
gdfile = ${MODEL_PATH}/${model}/${gdFile}
gdoutf = ${MODEL_PATH}/${model}/${gdFile}
gpack = none
!
gvcord = pres
glevel= 500
gfunc = sge(tmpk,271.16)
GRDNAM = tmax500@0%none
r

gvcord = pres
glevel= 850
gfunc = sge(tmpk,271.16)
GRDNAM = tmax850@0%none
r

gvcord=hght
glevel= 2
gfunc = sge(tmpk,271.16)
GRDNAM = tmax2m@0%none
r

gvcord = pres
glevel = 0
gvcord = none
gfunc = SMAX(tmax850, tmax500)
grdnam = tmax_500_850@0%none
r

gvcord = pres
glevel = 0
gvcord = none
gfunc = SMAX(tmax_500_850,tmax2m)
grdnam = tmax_500_850_2m@0%none
r

gvcord = pres
glevel= 500
gfunc = slt(tmpk,271.16)
GRDNAM = tmin500@0%none
r

gvcord = pres
glevel= 850
gfunc = slt(tmpk,271.16)
GRDNAM = tmin850@0%none
r

gvcord=hght
glevel= 2
gfunc = slt(tmpk,271.16)
GRDNAM = tmin2m@0%none
r

gvcord = pres
glevel = 0
gvcord = none
gfunc = SMAX(tmin500,tmin850)
grdnam = tmin_500_850@0%none
r

gvcord = pres
glevel = 0
gvcord = none
gfunc = SMAX(tmin_500_850,tmin2m)
grdnam = tmin_500_850_2m@0%none
r

gdfile=${MODEL_PATH}/${model}/${previousgdFile}
glevel = 0
gdattim = f${previous}
gvcord = none
gfunc = SWEM
grdnam = swem1
r

gdfile=${MODEL_PATH}/${model}/${gdFile}
gdattim = f${TIME}
glevel = 0
gvcord = none
gfunc = SWEM
grdnam = swem2
r

glevel = 0
gvcord = none
gfunc = SUB(swem1^F${previous},swem2^F${TIME})
grdnam = swemdiff
r

glevel = 0
gvcord = none
gfunc = ADD(12, MUL(2,SUB(271.16,tmax_500_850_2m@0%none)))
grdnam = tmaxrat
r

glevel = 0
gvcord = none
gfunc = ADD(12, SUB(271.16,tmin_500_850_2m@0%none))
grdnam = tminrat
r



e
EOFD

set previous = ${TIME}
rm last.nts
rm gemglb.nts

end

# MUL(quo(mul(SWEM@0%none,10),25.4),ADD(12, MUL(2,SUB(271.16,tmax_500_850_2m@0%none))))

# MUL(quo(mul(SWEM@0%none,10),25.4),ADD(12, SUB(271.16,tmin_500_850_2m@0%none)))
