# Usage ./tempf_adv.sh  <model>  <time1,time2,...>  <runTime>  <MODEL path>

echo "checking for params..."
if( $1 == "" || $2 == "" || $3 == "" || $4 == "") then
    echo "All 3 paremeters must be defined!"
    echo "Usage ./tempf_adv.sh  <model>  <time1,time2,...>  <runTime> <MODEL path>"
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
set variable = "tmpf_adv"
set gdFile = ${model}".gem"
#Set output Directory = Timestamp_model
set outDir = ${baseDir}/${model}/${timeStamp}
set MODEL_PATH  = $4 
set proj = "MER//NM"

# Make our run directory.
if !(-e ${outDir}) then
  mkdir -p ${baseDir}/${model}/${timeStamp}
  chmod 777 -R ${baseDir}/${model}/${timeStamp}
endif

foreach TIME ($times:q)

  set gdFile = ${runTime}"f"${TIME}".gem"

  # if (${model} == 'gfs' && ${TIME} > 192) then
  #   set gdFile = ${runTime}"_2p5.gem"
  # endif

  # if (${model} == 'gfs' && ${TIME} < 192 && ${TIME} > 120) then
  #   set gdFile = ${runTime}"_p5_2.gem"
  # endif

  # if (${model} == 'gfs' && ${TIME} < 192 && ${TIME} <= 120) then
  #   set gdFile = ${runTime}"_p5.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} > 60) then
  #   set gdFile = ${runTime}"_4.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} <= 60 && ${TIME} > 39) then
  #   set gdFile = ${runTime}"_3.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} <= 39 && ${TIME} > 18) then
  #   set gdFile = ${runTime}"_2.gem"
  # endif

  # if (${model} == 'nam' && ${TIME} <= 18) then
  #   set gdFile = ${runTime}"_1.gem"
  # endif

foreach level (850 700)

 set imgDir = ${baseDir}/${model}/${timeStamp}/${level}/${variable}
 mkdir -p ${baseDir}/${model}/${timeStamp}/${level}/${variable}

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

gdplot2_gf << EOF 
       
  GDFILE   = "${MODEL_PATH}/${model}/${gdFile}"
  GDATTIM  = "f${TIME}"
  CLEAR    = "n"
  GLEVEL   = "${level}"
  GVCORD   = PRES
  PANEL    = 0
  SKIP     = 0
  SCALE    = 4
  GDPFUN   = sm9s(adv(tmpf,wnd))
  TYPE     = f
  CONTUR   = 0
  CINT     = 0
  LINE     = 0
  FINT   = -12;-10;-8;-6;-4;-2; 0; 2; 4; 6; 8; 10; 12
  FLINE  =  30; 28;27;26;25;24; 0;0;10;17;16; 14;15;7
  HILO     =  
  HLSYM    =  
  WIND     = 
  REFVEC   =
  TEXT =  0
  TITLE = 0
  GAREA    = us
  IJSKIP   =  
  MSCALE   = 0
  LATLON   =                                                                 
  DEVICE = xw                                                                      
  STNPLT =                                                                         
  SATFIL =                                                                         
  RADFIL =     
  GAREA  = ${REGION}
  PROJ   = ${proj}                                                                             
  STREAM =   
  MAP = 0                                                                      
  POSN   =                                                                   
  COLORS = 2                                                                    
  MARKER=  0                                                                      
  GRDLBL=  0                                                                     
  LUTFIL=  none
  FILTER = yes
  CLRBAR   = 1/h/lc/.5;.01;.5;.01
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