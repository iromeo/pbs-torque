# MIT License
#
# Copyright (c) 2017 Silas Kieser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# See https://github.com/Snakemake-Profiles/generic/blob/master/hooks/post_gen_project.py

import os

TARGET = os.path.abspath(os.getcwd())

for root, dirs, files in os.walk(TARGET):
    for filename in files:
        # read file content
        with open(os.path.join(root, filename)) as f:
            content = f.read()
        # replace tag by install path
        content = content.replace('$((INSTALDIR))', TARGET)
        # replace file content
        with open(os.path.join(root, filename), 'w') as f:
            f.write(content)
