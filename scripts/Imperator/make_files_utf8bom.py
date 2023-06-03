import codecs

# Add UTF-8 with BOM encoding to a file.

def add_utf8_bom(filename):
	with codecs.open(filename, 'r', 'utf-8') as f:
		content = f.read()
	with codecs.open(filename, 'w', 'utf-8') as f2:
		f2.write('\ufeff')
		f2.write(content)
	return

files = [""]
path_to_mod = ""

for i in files:
	i = path_to_mod + i
	add_utf8_bom(i)
