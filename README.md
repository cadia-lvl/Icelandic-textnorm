# Haukur - Text normalization for Icelandic

THIS REPOSITORY IS STILL IN DEVELOPMENT, NOT YET A FUNCTIONAL TOOL!
--------------------------------------------------------------------

This text normalization toolkit can be used for the development of normalization grammars, and it contains a ready-to-use normalization application for Icelandic.
The normalization approach follows the idea of a two step process: classification and verbalization, as in Sparrowhawk (https://github.com/google/sparrowhawk). The implementation utilizes data structures and methods from Sparrowhawk's C++ code, but it is not a direct conversion. 

Haukur is designed for use in the Ossian TTS frontend library.

Installation
-------------

Haukur uses the following dependencies (see: requirements.txt):

- nltk >= 3.3
- openfst >= 1.6.9

Further, you need to download Pynini from http://www.openfst.org/twiki/bin/view/GRM/PyniniDownload
Unpack pynini into the site-packages folder of the virtual env where Haukur is run from, and install:

```sh
cd pynini-2.0.0
python3 setup.py install
python3 setup.py test
```

