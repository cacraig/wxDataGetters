from gemData import GemData
from batchGenerateImages import BatchGenerateImages
from gempak import Gempak
from optparse import OptionParser
from argparse import ArgumentParser

def main():

  parser = ArgumentParser()
  optparser = OptionParser()

  parser.add_argument("-b", "--batch", action='store_true',
                    help="Execute Batch image generation")

  #parser.add_argument("-nodata", "--nodata", action='store_true',
  #                  help="Skip Data Retrieval")

  args = parser.parse_args()

  # Initialize data getter
  dataGetter = GemData()
  
  # Retrieve and save data.
  dataGetter.getData()
  
  # Image Generation Block.
  if args.batch:
    gempak = Gempak(dataGetter)
    gempak.runGempakScripts()

  # Scrub all of our model data.
  dataGetter.scrubTreeData(dataGetter.constants.dataDirEnv)

if __name__ == "__main__":
  main()
