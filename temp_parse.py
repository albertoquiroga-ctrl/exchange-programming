import pathlib,re
text=pathlib.Path('temp_openrouter_docs.html').read_text()
match=re.search(r"curl\\s+-L\\s+'https://openrouter.ai/api/v1/chat/completions'(.*?)(?:</code>|$)",text,re.S)
print(match.group(1)[:400])
