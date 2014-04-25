from gemData import GemData
from batchGenerateImages import BatchGenerateImages
from optparse import OptionParser
from argparse import ArgumentParser
from subprocess import call

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
  #dataGetter.getData()
  
  # Image Generation Block.
  if args.batch:
    imageGenerator = BatchGenerateImages(dataGetter)
    cmd = imageGenerator.getCommand()
    call(cmd, shell=True)

if __name__ == "__main__":
  main()
