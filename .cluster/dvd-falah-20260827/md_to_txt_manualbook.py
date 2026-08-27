#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Konversi manual_book_draft.md -> .txt bersih (folder 05 DVD)."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\Falah\Documents\clustering-jobs\.cluster\dvd-falah-20260827\manual_book_draft.md'
DST = r'C:\Users\Falah\Documents\clustering-jobs\DELIVERY\DVD FALAH\202243502165_FALAH FAHRUROZI\05 - MANUAL BOOK\MANUAL BOOK - Dashboard Persebaran Peluang Kerja (DBSCAN).txt'

out = []
in_code = False
with open(SRC, encoding='utf-8') as f:
    for line in f.read().split('\n'):
        s = line.rstrip()
        # code fence
        if s.strip().startswith('```'):
            in_code = not in_code
            continue
        # heading: # -> BERSIH (teks saja), tambah garis pemisah
        m = re.match(r'^(#{1,6})\s+(.*)', s)
        if m:
            level = len(m.group(1))
            txt = m.group(2).strip()
            if level <= 2:
                out.append('')
                out.append(txt.upper())
                out.append('=' * min(len(txt), 60))
            else:
                out.append('')
                out.append(txt)
            continue
        # horizontal rule
        if re.match(r'^\s*---+\s*$', s):
            out.append('-' * 40)
            continue
        # bold/italic markers -> plain
        s2 = s.replace('**', '').replace('*', '')
        # tabel: rapikan pemisah (baris |---|) jadi garis
        if re.match(r'^\s*\|[\s:\-|]+\|\s*$', s2):
            continue
        out.append(s2 if s2.strip() else '')

text = '\n'.join(out)
# rapikan multi blank line
text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'
with open(DST, 'w', encoding='utf-8') as f:
    f.write(text)
print('OK:', DST, '| chars:', len(text))
