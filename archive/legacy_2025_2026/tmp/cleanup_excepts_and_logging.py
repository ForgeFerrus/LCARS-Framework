#!/usr/bin/env python3
import os, re, ast, tokenize, token, io
from pathlib import Path

root = Path(r"C:/Users/Forge/MyProject/LCARS-Framework")
skipdirs = {'.git','__pycache__','archive','archives','.venv','tmp'}
allowed_methods = {'info','warning','error','exception','debug','critical'}

changed_files = []

# Regex replacements for bare except
pattern_bare_line = re.compile(r"^(?P<indent>[ \t]*)except:\s*(?P<comment>#.*)?$", flags=re.MULTILINE)
pattern_bare_inline = re.compile(r"^(?P<indent>[ \t]*)except:\s*(?P<stmt>pass|return\b.*)$", flags=re.MULTILINE)

for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in skipdirs]
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        fp = Path(dirpath) / fn
        rel = fp.relative_to(root)
        try:
            text = fp.read_text(encoding='utf-8')
        except Exception:
            continue
        new_text = text
        # Replace bare except lines
        new_text = pattern_bare_line.sub(lambda m: f"{m.group('indent')}except Exception: {m.group('comment') or ''}".rstrip(), new_text)
        # Handle inline except: pass -> except Exception:\n    pass
        def repl_inline(m):
            indent = m.group('indent')
            stmt = m.group('stmt')
            return f"{indent}except Exception:\n{indent}    {stmt}"
        new_text = pattern_bare_inline.sub(repl_inline, new_text)

        # Now tokenize to sanitize logging string literals
        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(new_text).readline))
        except Exception:
            # fallback: skip file
            continue
        modified = False
        out_tokens = []
        i = 0
        N = len(tokens)
        while i < N:
            tok = tokens[i]
            out_tokens.append((tok.type, tok.string))
            # detect logger or logging method pattern
            if tok.type == token.NAME and tok.string in ('logger', 'logging'):
                # look ahead for ., NAME(method), '(', STRING
                j = i+1
                # skip any spacing tokens are captured as NL/NEWLINE but generate_tokens yields them
                if j < N and tokens[j].type == token.OP and tokens[j].string == '.':
                    if j+1 < N and tokens[j+1].type == token.NAME and tokens[j+1].string in allowed_methods:
                        # find '(' token
                        k = j+2
                        while k < N and tokens[k].type in (tokenize.NL, tokenize.NEWLINE, token.INDENT, token.DEDENT):
                            k += 1
                        if k < N and tokens[k].type == token.OP and tokens[k].string == '(':
                            if k+1 < N and tokens[k+1].type == token.STRING:
                                s_tok = tokens[k+1]
                                sraw = s_tok.string
                                # skip f-strings
                                prefix_match = re.match(r"(?P<prefix>[rubfRUBF]*)(?P<quote>['\"]{1,3}).*", sraw, flags=re.DOTALL)
                                prefix = prefix_match.group('prefix') if prefix_match else ''
                                if 'f' in prefix.lower():
                                    # skip f-strings
                                    pass
                                else:
                                    # try to literal_eval
                                    try:
                                        sval = ast.literal_eval(sraw)
                                    except Exception:
                                        sval = None
                                    if isinstance(sval, str):
                                        sanitized = ''.join(ch for ch in sval if ord(ch) < 128)
                                        if sanitized != sval:
                                            # replace token string with repr(sanitized)
                                            out_tokens.pop()  # remove last appended (the logger token), we'll re-append sequence starting at i
                                            # append tokens from i to k (inclusive) as original
                                            for t2 in tokens[i:k+1]:
                                                out_tokens.append((t2.type, t2.string))
                                            # append new string token
                                            out_tokens.append((token.STRING, repr(sanitized)))
                                            # advance i to skip original string token
                                            i = k+1
                                            modified = True
                                            i += 1
                                            continue
            i += 1
        if modified:
            # reconstruct source
            try:
                new_src = tokenize.untokenize(out_tokens)
            except Exception:
                continue
            if new_src != new_text:
                new_text = new_src
        # if anything changed, write back
        if new_text != text:
            try:
                fp.write_text(new_text, encoding='utf-8')
                changed_files.append(str(rel))
            except Exception:
                pass

# Print summary
print('Modified files count:', len(changed_files))
for f in changed_files[:200]:
    print(' ', f)
