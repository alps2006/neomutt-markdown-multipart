#!/usr/bin/env python3

"""
File: markdownmail.py
Author: alps2006
Email: guoxiangxun@gmail.com
Github: https://github.com/alps2006
Description: convert markdown file to multipart/related mail for neomutt.
"""

import fileinput
import sys
import os
import uuid
import re


def write_txt(md_filename, out_filename):
    os.system('pandoc -f markdown-blank_before_blockquote-blank_before_header -t plain -o {0} {1}'.format(out_filename, md_filename))


def write_html(md_filename, out_filename):
    os.system('pandoc -s -f markdown-blank_before_blockquote-blank_before_header --resource-path ~/.local/share/templates/ --template email -o {0} {1}'.format(out_filename, md_filename))

def convert_to_inline_html(html_filename, out_filename):
    """ rewrite html img src url to mail cid """

    related_cid = {}
    with open(html_filename, 'r') as f_in:
        lines = f_in.read()

    # findall <img> src list and set key-value(uuid) in each item
    src_list = re.findall(r'<img\n?\s*src="(.*?)"', lines)
    for item in set(src_list):
        related_cid[item] = uuid.uuid4().hex
        lines = re.sub(item, 'cid:' + related_cid[item], lines)

    with open(out_filename, 'w') as f_out :
        f_out.write(lines)
    return related_cid


def write_macro_instructions(plain_filename, html_filename, related_cid, out_filename):

    instructions = 'push ';
    if len(related_cid) == 0:
        instructions += '<attach-file>{0}<enter><toggle-disposition><tag-entry><attach-file>{1}<enter><toggle-disposition><tag-entry><group-alternatives>'.format(plain_filename, html_filename)
    else:
        instructions += '<attach-file>{0}<enter><toggle-disposition><tag-entry><attach-file>{1}<enter><toggle-disposition><tag-entry><group-alternatives><tag-entry>'.format(plain_filename, html_filename)
        for k,v in related_cid.items():
            # clear existed content-id by '^u' before setting a new
            instructions += '<attach-file>{0}<enter><toggle-disposition><edit-content-id>^u{1}<enter><tag-entry>'.format(k, v)
        else:
            instructions += '<group-related>'
    with open(out_filename, 'w') as f:
        f.write(instructions)
    return instructions


def main():
    TXT_FILENAME = '/tmp/msg.txt'
    HTML_FILENAME = '/tmp/msg.html'
    HTML_INLINE_FILENAME = '/tmp/msg_inline.html'
    MACRO_FILENAME = '/tmp/msg.macro'

    with open(TXT_FILENAME, 'w') as f, sys.stdin as f2:
        f.write(f2.read())

    write_html(TXT_FILENAME, HTML_FILENAME)
    write_txt(TXT_FILENAME, TXT_FILENAME)
    related_cid = convert_to_inline_html(HTML_FILENAME, HTML_INLINE_FILENAME)
    return write_macro_instructions(TXT_FILENAME, HTML_INLINE_FILENAME, related_cid, MACRO_FILENAME)

if __name__ == "__main__":
    main()
