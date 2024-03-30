EOF_MARKER = b'%%EOF'
file_name = 'plantillasPDF/plantillaVaciaDigital.pdf'

with open(file_name, 'rb') as f:
    contents = f.read()

# check if EOF is somewhere else in the file
if EOF_MARKER in contents:
    # we can remove the early %%EOF and put it at the end of the file
    contents = contents.replace(EOF_MARKER, b'')
    contents = contents + EOF_MARKER
else:
    # Some files really don't have an EOF marker
    # In this case it helped to manually review the end of the file
    print(contents[-8:]) # see last characters at the end of the file
    # printed b'\n%%EO%E'
    contents = contents[:-6] + EOF_MARKER

with open(file_name.replace('.pdf', '') + '_fixed.pdf', 'wb') as f:
    f.write(contents)