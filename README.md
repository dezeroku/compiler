Compiler project for Formal Languages & Translation Techniques 2018

## About
It's written in Python3, all required libraries can be installed using setup.sh (Ubuntu 18.04).

Running 'make' is necessary to compile interpreter, which is used in some optimalisations.

It's not really the best Python you can write, it has some globals etc. but it gets the job done.

PLY is used for lexing/parsing.

spec.pdf contains language grammar, info etc. (in Polish).

## Build

You can build Docker image by calling
```
docker build -t image_name .
```

when in repo root directory.

## How to use
```
python3 compilator.py input_name output_name
```

If you have source code in current directory, you can run dockerized version with something like:
```
docker run -v $(pwd):/usr/src/app/code image_name ./kompilator code/temp_2.imp code/result
```

Current directory has to be mounted as subfolder, otherwise it won't work.

Run
```
python3 compilator.py -h
```
for more options.

## Tests
Run tests either by calling 
```
pytest
```

in case of normal installation, or
```
docker run image_name python3.7 -m pytest

```

in case of dockerized version.
