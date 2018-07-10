#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

if __name__ == "__main__":
    subprocess.run(['python3', '-m', 'unittest', 'discover', '-s', './test'])
