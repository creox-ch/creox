"""After typograf: keep punctuation glued to the wrapped hyphen word / nobr span, so a comma never starts a line."""
import re, sys, pathlib
P1 = re.compile(r'(<span style="display:inline-block;max-width:100%">(?:(?!</span></span>).)*?)</span></span>([.,:;!?)]+)', re.S)
P2 = re.compile(r'(<span class=[\'"]nobr[\'"]>[^<]*)</span>([.,:;!?)]+)')
for f in sys.argv[1:]:
    t = pathlib.Path(f).read_text()
    n = P1.sub(r'\1\2</span></span>', t); n = P2.sub(r'\1\2</span>', n)
    if n != t: pathlib.Path(f).write_text(n)
