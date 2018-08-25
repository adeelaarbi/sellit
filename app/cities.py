# coding: utf-8
#
# The World Gazetteer provides a downloadable file that contains a list
# of all cities, towns, administrative divisions and agglomerations with
# their population, their English name parent country.
#
# Article:  http://answers.google.com/answers/threadview/id/774429.html
# Download: http://www.world-gazetteer.com/dataen.zip


import codecs


# can't just iterate over the fd as there are many lines with
# carriage returns in the middle of the line and things break.
def rows(fd):
    n = 1
    rest = ""
    while 1:
        chunk = fd.read(1024).encode("utf-8")
        if not chunk:
            break

        while 1:
            chunk = rest + chunk
            pos = chunk.find("\n")
            if pos > -1:
                pos += 1
                line, rest = chunk[:pos], chunk[pos:]
                yield n, line.replace("\r", "").replace("\n", "").split("\t")
                chunk = ""
                n += 1
            else:
                break


def get_citites():
    cities = set()
    fd = codecs.open("dataen.txt", "r", "utf-8")
    for n, row in rows(fd):
        columns = [row[8], row[9], row[1]]  # Country,Region,City
        if all(columns):
            cities.add(",".join(columns))

    for line in sorted(cities):
        print (line)
