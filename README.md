# Symbolicate

Symbolicate macOS or iOS crash reports easily.

This script simply uses `atos` XCode tool to symbolicate crash reports as explained here:
https://developer.apple.com/library/archive/technotes/tn2151/_index.html#//apple_ref/doc/uid/DTS40008184-CH1-SYMBOLICATE_WITH_ATOS

## Requirements

* XCode
* Python3

## Usage

```
$ python3 symbolicate.py --help
Usage: symbolicate.py [options]. symbolicate.py -h for help.

Options:
  -h, --help            show this help message and exit
  -c FILE, --crash=FILE
                        Path to the .crash file
  -d DIR, --dsym=DIR    Path to the folder with dSYM files
  -o FILE, --output=FILE
                        Path to the output file with the symbolicated crash
  -a ARCH, --arch=ARCH  Target architecture
```

Example:

```
python3 symbolicate.py -c test.crash -d test.xcarchive/dSYMs -a x86_64 -o test_symbolicated.crash
```