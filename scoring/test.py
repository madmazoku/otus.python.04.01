#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from optparse import OptionParser

if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-v", "--verbose", action="store_true", default=False)
    (opts, args) = op.parse_args()
    test_args = ['python3', '-m', 'unittest', 'discover', '-s', './test']
    if opts.verbose:
        test_args.append('-v')
    subprocess.run(test_args)
