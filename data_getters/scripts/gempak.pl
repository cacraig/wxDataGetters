#! /usr/bin/perl

# usage perl gempak.pl <gfs=gfsfile.gem> <nam=namfile.gem>
use Data::Dumper;
use Cwd;

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
    print "exists";
    $validModels{$splitArg[0]} = $splitArg[1];
  }
  else
  {
    print "Invalid Model passed! Check your parameters, dude!\nTried to pass ".$splitArg[0]."\n";
  }
}


# Get all scripts from gempak dir.
#@files = <gempak/*.sh>;

$rucTimes    = '00,01,02,03';
$gfsTimes    = '00,06,12,18';
$namTimes    = '00,06,12,18';
$ukmetTimes = '00,06,12,18';
$ecmwfTimes  = '';

%modelForecastTimes = (
  'ruc'   => $rucTimes,
  'gfs'   => $gfsTimes,
  'nam'   => $namTimes,
  #'ecmwf' => @ecmwfTimes,
  'ukmet' => $ukmetTimes 

);

# If we are in the parent directory, lets see if we can get into scripts, and execute.
print $#files;
if(!@files)
{
  chdir('scripts');
  @files = <gempak/*.sh>;
  print $#files;
  if($#files < 0)
  {
    print "No gempak scripts can be located in /scripts. Assure that there are scripts to be had!\n";
  }
}


#Iterate through each script, and times. Execute gempak scripts foreach model, and times.
foreach $key (keys \%modelForecastTimes)
{
  foreach $file (@files) 
  {
    $outfile = '';
    if($validModels{$key})
    {
      $cmd =  $file." ".$key." ".$modelForecastTimes{$key}." ".$validModels{$key}."\n";
      print "\n".$cmd;
      `$cmd`;
    }
  }
}
