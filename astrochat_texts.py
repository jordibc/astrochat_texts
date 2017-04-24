#!/usr/bin/python3

"""
Extrae los textos de astrochat a partir de los xml generados por Construct 2.
"""

import sys
import os
import re
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add = parser.add_argument  # shortcut
    add('files', metavar='FILE', nargs='+', help='fichero xml con los textos')
    add('--overwrite', action='store_true',
        help='no comprobar si el fichero de salida existe')
    args = parser.parse_args()

    for fname in args.files:
        outfname = '%s.txt' % fname
        if not args.overwrite:
            check_if_exists(outfname)
        extract(fname, outfname)


def extract(fname, outfname):
    "Extract the contents of the xml file fname into file outfname"
    print('Processing file %s ...' % fname)
    with open(outfname, mode='wt', encoding='utf8') as out:
        for line in get_content(fname):
            out.write(line)
    print('The output is in file %s' % outfname)


def get_content(fname):
    "Yield text corresponding to any of the keywords in the xml file"
    # Go thru al the lines of the file and yield after a line with a "keyword".
    keywords = [('respuesta', 'name="Set text"'),
                ('chat', 'action behavior="Typing"')]
    coming = None
    for line in open(fname, encoding='utf8'):
        if coming:
            if '>&quot;' in line and not '>&quot;&quot;<' in line:
                contents = clean(line).split('>&quot;', 1)[1].split('&quot;')[:-1]
                yield '[%s]\n%s\n\n' % (coming, '\n'.join(contents))
            coming = None
        else:
            for coming, keyword in keywords:
                if keyword in line:
                    break
            else:
                coming = None


def clean(txt):
    "Replace all the escape sequences for something appropriate"
    silent_replacements = [
        ('&quot;&quot;&quot;', '&quot;"'),  # in case it starts with "
        ('&quot;&quot;', '"'),
        ('&apos;', "'"),
        ('&amp; *newline *&amp;', ''),
        ('&quot; *&amp; *Name *&amp; *&quot;', '<name>')]
    for x, y in silent_replacements:
        txt = re.sub(x, y, txt)

    suspicious_chars = ['&#x0D;', '&#x0A;']
    for x in suspicious_chars:
        if x in txt:
            print('Warning: suspicious character found (%s)' % x)
            txt = txt.replace(x, '')

    return txt


def check_if_exists(fname):
    if os.path.exists(fname):
        answer = input('File %s already exists. Overwrite? [y/n] ' % fname)
        if not answer.lower().startswith('y'):
            sys.exit('Cancelling.')


if __name__ == '__main__':
    main()
