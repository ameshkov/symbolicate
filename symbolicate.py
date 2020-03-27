#!/usr/bin/python3

import subprocess
import sys
import optparse
import os
import re

parser = optparse.OptionParser(usage="%prog [options]. %prog -h for help.")
parser.add_option("-c", "--crash", dest="crash_file",
                  help="Path to the .crash file", metavar="FILE")
parser.add_option("-d", "--dsym", dest="dsym_dir",
                  help="Path to the folder with dSYM files", metavar="DIR")
parser.add_option("-o", "--output", dest="output_file",
                  help="Path to the output file with the symbolicated crash", metavar="FILE")
parser.add_option("-a", "--arch", dest="arch", help="Target architecture", metavar="ARCH")
(options, args) = parser.parse_args(sys.argv)

if not options.crash_file:
    parser.error('Crash file must be specified')

if not options.dsym_dir:
    parser.error('dSYM folder must be specified')

if not options.output_file:
    parser.error('Output file path must be specified')

if not options.arch:
    parser.error('Please specify the architecture (x86_64 or arm64)')

if not os.path.exists(options.crash_file):
    raise ValueError("{0} does not exist!".format(options.crash_file))

if not os.path.exists(options.dsym_dir):
    raise ValueError("{0} does not exist!".format(options.dsym_dir))

if not os.path.isdir(options.dsym_dir):
    raise ValueError("{0} is not a directory!".format(options.dsym_dir))


def try_symbolicate_local_addr(load_addr, address, dwarf_path):
    result = subprocess.run([
        "atos",
        "-o",
        dwarf_path,
        "-l",
        load_addr,
        address
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = result.stdout.decode("utf-8").strip()
    if result.returncode != 0:
        return ""

    if load_addr in out or address in out:
        # Something went wrong if this happened
        return ""

    print("Symbolicated {0} {1} to {2}".format(load_addr, address, out))
    return out


def symbolicate_local_addr(load_addr, address):
    # go through all dSYM
    dsym_dirs = os.listdir(options.dsym_dir)
    for dir_name in dsym_dirs:
        dsym_dir = os.path.join(options.dsym_dir, dir_name)
        if not os.path.isdir(dsym_dir):
            continue

        dwarf_dir = os.path.join(dsym_dir, 'Contents/Resources/DWARF')
        for filename in os.listdir(dwarf_dir):
            dwarf_file = os.path.join(dwarf_dir, filename)
            if os.path.isfile(dwarf_file):
                symbolicated = try_symbolicate_local_addr(
                    load_addr, address, dwarf_file)
                if symbolicated != "":
                    return symbolicated

    return ""


def symbolicate_line(line):
    p = re.compile('[0-9]+ .*((0x[0-9a-f]+) (0x[0-9a-f]+)).*')
    m = p.match(line)

    if not m:
        return line

    load_addr = m.group(3)
    address = m.group(2)

    symbolicated_local_addr = symbolicate_local_addr(load_addr, address)
    if symbolicated_local_addr != "":
        line = line.replace(m.group(1), symbolicated_local_addr)

    return line


with open(options.crash_file, 'r') as file:
    crash = file.read()

output = []
lines = crash.splitlines()

for line in lines:
    symbolicated_line = symbolicate_line(line)
    output.append(symbolicated_line)

with open(options.output_file, "w") as file:
    file.write("\n".join(output))

print(
    "Finished symbolicating, the output has been written to {0}".format(options.output_file))
