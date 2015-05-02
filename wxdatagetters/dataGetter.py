from processors.dataProcessor import DataProcessor
from generators.gempak import Gempak
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
    modelClass = getModelObj(args.model)
    modelLinks = modelClass.getRun()
    # initalize for only one model.
    dataGetter = DataProcessor(modelClass, True) # Second parameter enables DEBUG mode.
    dataGetter.getData(modelLinks)

  # # Retrieve and save data.
  
  print "Trying batch"
  # Image Generation Block.
  if args.batch:
      gempak = Gempak(dataGetter)
      gempak.doThreadedGempakScripts(modelLinks)

  # Scrub all of our model data.
  if args.clean:
    if args.model:
      dataGetter.scrubTreeData(dataGetter.constants.dataDirEnv + "/" + args.model)
    else:
      dataGetter.scrubTreeData(dataGetter.constants.dataDirEnv)

def getModelObj(model):
  model = model.capitalize() # Capitalize for classname.
  import_module_ = "models." + model
  model_class = model
  module = __import__(import_module_, fromlist = [model])
  try:
    class_ = getattr(module, model_class)()
  except AttributeError:
    print 'Class does not exist'
  return class_


if __name__ == "__main__":
  main()



