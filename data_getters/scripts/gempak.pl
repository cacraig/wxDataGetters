#! /usr/bin/perl

# usage perl gempak.pl <gfs=gfsfile.gem> <nam=namfile.gem>
use Data::Dumper;

# Initialize env vars.
$res = `. /home/cacraig/gempak/GEMPAK7/Gemenviron.profile`;

$modelDataPath = $ENV{'MODEL'};

# All valid models.
%validModels = ('nam'=> '', 'gfs'=>'', 'ukmet'=>'', 'ruc'=>'', 'ecmwf' =>'');

# Set $models[model] = (fileName)
foreach(@ARGV)
{
  @splitArg = split(/=/, $_);
  # Check if we passed a valid model, else skip.
  if(exists $validModels{$splitArg[0]})
  {
    $validModels{$splitArg[0]} = $splitArg[1];
  }
  else
  {
    print "Invalid Model passed! Check your parameters, dude!\nTried to pass ".$splitArg[0]."\n";
  }
}

print Dumper(%validModels);

# Get all scripts from gempak dir.
@files = <./gempak/*.sh>;

$rucTimes    = '00,01,02,03';
$gfsTimes    = '00,03,06,12';
$namTimes    = '00,03,06,12';
$ukmentTimes = '00,03,06,12';
$ecmwfTimes  = '';

%modelForecastTimes = (
  'ruc'   => $rucTimes,
  'gfs'   => $gfsTimes,
  'nam'   => $namTimes,
  #'ecmwf' => @ecmwfTimes,
  'ukmet' => $ukmetTimes 

);

#Iterate through each script requiring level.
foreach $key (keys \%modelForecastTimes)
{
  foreach $file (@files) 
  {
    $outfile = '';
    print $key."!!!\n";
    print $validModels{$key}."\n";
    if($validModels{$key})
    {
      $cmd =  $file." ".$key." ".$modelForecastTimes{$key}." ".$validModels{$key}."\n";
      print $cmd;
    }
  }
}
