wxDataGetters
=============

wx Model Data Getters

Retrieves model data from various sources, downloads them, and processes them.
All images will be stored in the scripts/data.


Dependencies:
- BeautifulSoup
- Matplotlib >1.2
- Gempak >7.0.0
- dcgrib2

To execute: 
##### python dataGetter.py [--batch] [--model=...]

     optional arguments:

       -h, --help   show this help message and exit

       --model=...  Name of model to retrieve.

       -b, --batch  Execute Batch image generation
