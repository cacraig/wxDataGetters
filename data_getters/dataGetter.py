from gemData import GemData
from gempak import Gempak
from optparse import OptionParser
from argparse import ArgumentParser
import ConfigParser


# Usage : python dataGetter.py -dev -b --clean
# [ONE MODEL] : python dataGetter.py -b -dev --model gfs 
def main():

  parser = ArgumentParser()
  optparser = OptionParser()

  parser.add_argument("-b", "--batch", action='store_true',
                    help="Execute Batch image generation")

  # parser.add_argument("-prod", "--prod", action='store_true',
  #                   help="Optional build command for prod env ngwips.")

  # parser.add_argument("-dev", "--dev", action='store_true',
  #                 help="Optional build command for dev env ngwips.")

  parser.add_argument("-c", "--clean", action='store_true',
                help="Optional command to clean all of the data directories.")

  parser.add_argument("-m", "--model", required=False,
                help="Only process one model.")

  args = parser.parse_args()

  if args.model:
    # initalize for only one model.
    dataGetter = GemData(args.model)
  else:
    # Initialize data getter
    dataGetter = GemData()

  # # Retrieve and save data.
  dataGetter.getData()
  print "Trying batch"
  # # Image Generation Block.
  if args.batch:
      gempak = Gempak(dataGetter)
      gempak.runGempakScripts()

  # Scrub all of our model data.
  if args.clean:
    dataGetter.scrubTreeData(dataGetter.constants.dataDirEnv)

  if args.model:
    #dataGetter.transferFilesToProd(args.model)
    return

  # if args.prod:
  #   dataGetter.mvAssets()
  #   dataGetter.rebuild('prod')
  # elif args.dev:
  #   dataGetter.mvAssets()
  #   dataGetter.rebuild('dev')

  #dataGetter.transferFilesToProd()



if __name__ == "__main__":
  main()
