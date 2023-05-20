#!/usr/bin/env python3

# EPG merger
# Created by:  @thefirefox12537

import glob
import shutil
import requests
import threading
import os, re, sys
import xml.dom.minidom as dom
import lxml.etree as et

source = ''.join(sys.argv[2])
result = ''.join(sys.argv[1])
caption_name = ''.join(sys.argv[3])
caption_url = ''.join(sys.argv[4])
tmpdir = os.sep.join(["..", "tmp"])

def merge(tree, tagname):
    print(f"Merging {tagname}...")
    files =  glob.glob(os.sep.join([tmpdir, "*.xml"]))
    for file in files:
        root = et.parse(file).getroot()
        for child in root:
            if tagname in child.tag:
                tree.append(child)

def main():
    files = []
    urls = []

    if os.path.exists(result):
        os.remove(result)
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    if not os.path.exists(source):
        print(f"{source} is not exist")
        sys.exit(1)
    with open(source, mode="r") as epg:
        for text in epg.read().split('\n'):
            if re.findall(r'^http.*.xml', text):
                urls.append(text)
            elif not re.findall(r'^$', text):
                files.append(text)
    for url, name in zip(urls, files):
        epgxml = os.sep.join([tmpdir, name])
        if not os.path.exists(epgxml):
            print(f"Downloading {name}...")
            get = requests.get(url, allow_redirects=True).content
            open(epgxml, mode="wb").write(get)

    comment = {}
    comment["generator-info-name"] = f"EPG generated by {caption_name}"
    comment["generator-info-url"] = caption_url

    tree = et.Element("tv", comment)
    merge(tree, tagname="channel")
    merge(tree, tagname="programme")

    print("Parsing data...")
    tostring = et.tostring(tree, encoding="UTF-8", method="xml", xml_declaration=True)
    parsestring = dom.parseString(tostring).toprettyxml(indent="", encoding="UTF-8")
    output = re.sub(b'\n\n', b'', parsestring)

    print("Creating file...")
    with open(result, mode="wb") as epg:
        epg.write(output)
        epg.close()

    print("Removing temporary files...")
    shutil.rmtree(tmpdir)

if __name__ == "__main__":
    main()
    sys.exit()
