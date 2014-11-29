#! /usr/bin/env python

# Update:  15 Nov 2004 (rsk):  Added changes to support proper escaping of
# the % and & characters.
# Support for the courier option in submission format.

# Update:  12 Feb 2005 (rsk): Added code to remove writer comments
# delimited by [] (brackets)

# Update:  15 Mar 2005 (rsk): Change processing to read an outline file to
# determine which files to process.  # delimits sections and each new file is
# assumed to be a new section.

import sys
import os
import getopt
import re
import stat

def get_val(a,o):
    if len(o) > 2:
        return o[2:]
    return a.pop(0)

class NovelFile(object):
    def __init__(self, chapter, section, filename=None, description=None):
        self.chapter = int(chapter)
        self.section = int(section)
        self.filename = filename
        self.description = description
        pass

    def __cmp__(self, obj):
        try:
            hasattr(obj, "chapter")
            hasattr(obj, "section")
            pass
        except AttributeError as e:
            print "%s doesn't appear to be a NovelFile object." % repr(obj)
            raise e
        if self.chapter > obj.chapter:
            return 1
        if self.chapter < obj.chapter:
            return -1
        if self.section > obj.section:
            return 1
        if self.section < obj.section:
            return -1
        return 0

    def __repr__(self):
        return "<NovelFile instance: chapter %i, section %i, filename %s>" % (
            self.chapter, self.section, repr(self.filename))

    def open(self, mode=None):
        if mode == None:
            return open(self.filename)
        return open(self.filename, mode)
    
    
    pass

def sort_outline_file(outline_file = "outline.txt", dir="./", strict=1):
    if dir[-1] != "/":
        dir = dir + "/"
        pass
    try:
        ofh = open(outline_file)
        pass
    except IOError:
        print "Can't open outline file %s." % outline_file
        return None
    lineno =  0
    nflist = []
    for rec in ofh:
        lineno += 1
        rec = rec.strip()
        if rec.startswith("#"):
            continue
        if rec == "":
            continue
        array = rec.split(None, 3)
        if len(array) < 3:
            print "--"
            print rec
            print "Can't interpret outline record in line %i of file %s. Skipping." % (lineno, outline_file)
            continue
        chapter = array[0]
        section = array[1]
        file = array[2]
        desc = ""
        if len(array) > 3: desc = array[3]
        
        bad_chapter = 0
        bad_section = 0
        try:
            chapter = int(chapter)
            pass
        except ValueError:
            print "--"
            print "Bad chapter identifier '%s' in line %i of file %s." % (chapter, lineno, outline_file)
            bad_chapter = 1
            pass
        try:
            section = int(section)
            pass
        except ValueError:
            print "--"
            print "Bad section identifier '%s' in line %i of file %s." % (section, lineno, outline_file) 
            bad_section = 1
            pass
        if bad_chapter or bad_section:
            print "Skipping the preceding line."
            continue
        try:
            os.stat(dir + file)
            pass
        except OSError:
            if strict:
                print "--"
                print "Can't open file %s specified in line %i of file %s. Skipping." % (file, lineno, outline_file)
                continue
            pass
        new_nf = NovelFile(chapter, section, file, desc)
        nflist.append(new_nf)
        pass
    nflist.sort()
    return nflist
            
def usage():
    print """makesub [-snT -q(smart|dumb) -c word_count] -t options-file
    -o outputfile -d dirspec inputfile

    Where:

    inputfile is the file that contains the story.  For short stories this
    is the actual text of the file and is required.  For novels, this file
    is an outline file, which is a metafile describing which files contain
    the story and the order they occur in.  For novels, it is optional and
    defaults to "outline.txt".

    -t options file.  Where to find author, title, word count, and other
    information.

    -o the output LaTeX file.

    -s specifies that this is a submission output.

    -n Use the novel format instead of the short story format.

    -T suppress the title page output.

    -d Read novel files (not the outline) from the specified directory

    -q Specify a quotation mark handling method.

    -c supply a word count to the program.  If this argument is not specified,
    the program will calculate one (rounded to the nearest 100 words) for you.

    -h Show this message
"""

if __name__ == "__main__":
    if sys.argv[0].endswith("makesub3"):
        print "WARNING: makesub3 deprecated. Use makesub instead."
        pass
    rtncode = 0
    infile = []
    outfile = None
    tagfile = "./header.txt"
    submission = 0
    novel = 0
    smart = 0
    dumb = 0
    notitle = 0
    quotes = None
    supplied_wc = None
    try:
        (opts, inputargs) = getopt.getopt(sys.argv[1:], "snTq:t:o:c:d:h")
        pass
    except getopt.GetoptError:
        print "Unrecognized option."
        usage()
        sys.exit(1)
        pass
    noveldir = "./"
    nd_set = 0
    for opt in opts:
        if opt[0] == "-o":
            if outfile != None:
                print "Only one output file may be specified."
                usage()
                sys.exit(1)
                pass
            else:
                outfile = opt[1]
                pass
            pass
        if opt[0] == "-t":
            tagfile = opt[1]
            pass
        if opt[0] == "-s":
            submission = not submission
            pass
        if opt[0] == "-c":
            supplied_wc = int(opt[1])
            pass
        if opt[0] == "-n":
            novel = not novel
            pass
        if opt[0] == "-T":
            notitle = not notitle
            pass
        if opt[0] == "-q":
            quotes == opt[1]
            pass
        if opt[0] == "-h":
            usage()
            sys.exit(1)
            pass
        if opt[0] == "-d":
            nd_set = 1 
            noveldir = opt[1]
            pass
        pass

    infile = inputargs

    if len(infile) == 0 and not novel:
        print "Must specify at least one input file."
        usage()
        sys.exit(1)
        pass

    if novel:
        if len(infile) == 0:
            outline = "outline.txt"
            pass
        else:
            outline = infile[0]
            pass
        try:
            nd_stat = os.stat(noveldir)
            pass
        except OSError:
            print "Could not open %s directory." % noveldir
            sys.exit(1)
            pass
        if not stat.S_ISDIR(nd_stat[stat.ST_MODE]):
            print "%s not a directory." % noveldir
            sys.exit(1)
            pass
        infile = []  # wipe the infiles because we are recomputing
        infile = sort_outline_file(outline, noveldir)
        if infile == None:
            sys.exit(1)
            pass
        pass
        
    
    
    if outfile == None:
        print "Must specify output file."
        usage()
        sys.exit(1)
        pass
    if quotes not in ("smart", "dumb", None):
        print "-q must be 'smart' or 'dumb'"
        usage()
        sys.exit(1)
        pass
    if tagfile != None:
        try:
            tf = open(tagfile)
            pass
        except IOError as e:
            print "Can't open tag file '%s': %s" % (tagfile, e.strerror)
            usage()
            sys.exit(1)
            pass
        tfcont = "".join(tf.readlines())
        tf.close()
        pass
    else:
        tfcont = ""
        pass

    try:
        ouf = open(outfile, "w")
        pass
    except IOError as e:
        print "Can't open output file '%s': %s" % (outfile, e.strerror)
        usage()
        sys.exit(1)
        pass

    inputfiles = []
    inwordcount = 0
    for i in infile:
        try:
            if not novel:
                fname = i
                inputfiles.append((open(i), i))
                pass
            else:
                fname = noveldir + "/" + i.filename
                inputfiles.append((open(fname), i.filename, i))
                pass
            if supplied_wc == None:
                word_count_file = os.popen("wc -w < %s" % fname)
                inwordcount = inwordcount + int(word_count_file.readline())
                word_count_file.close
                pass
            pass
        except IOError:
            print "Can't open input file '%s'... skipping it and hoping for the best." % fname
            pass
        pass

    if supplied_wc != None:
        inwordcount = supplied_wc
        pass
    else:
        inwordcount = ((inwordcount + 50) / 100) * 100
        pass
    

    if len(inputfiles) == 0:
        if len(infile) == 1:
            print "Couldn't open input file."
            usage()
            sys.exit(1)
            pass
        else:
            print "Couldn't open any input files."
            usage()
            sys.exit(1)
            pass
        pass

    docopt = []
    if submission:
        docopt.append("courier")
        pass
    else:
        docopt.append("nonsubmission")
        pass
    
    if novel:
        docopt.append("novel")
        pass
    if notitle:
        docopt.append("notitle")
        pass
    if quotes != None:
        docopt.append(quotes)
        pass

    docopts = ""
    if len(docopt) > 0:
        docopts = docopt[0]
        for i in docopt[1:]:
            docopts = docopts + "," + i
            pass
        pass
    
    tag_file_constants = {"wordcount": inwordcount}
    
    ouf.write(
        """\\documentclass[%s]{sffms}
%s
\\begin{document}
""" % (docopts, tfcont % tag_file_constants))
    lastfile = None
    in_ul = 0
    ignore = 0
    curchap = None
    for inf in inputfiles:
        comment_count = 0
        if in_ul:
            print "Warning! New file while in emphasis. Possible runaway emphasis from %s" % lastfile
            rtncode = 2
            pass
        if ignore:
            print "Warning! New file while in comment mode. Possible runaway [ from %s" % lastfile
            rtncode = 2
            pass
        in_ul = 0
        lineno = 0
        ignore = 0
        cur_brack = "["
        line = inf[0].readline()
        lineno = lineno+1
        if novel:
            if inf[2].chapter != curchap:
                ouf.write("\\chapter{}\n")
                pass
            else:
                ouf.write("\n\\newscene\n\n")
                pass
            curchap = inf[2].chapter
            pass
        while (line):
            if line[0] == "#":
                line = "\n\\newscene\n\n"
                if in_ul == 1:
                    print "WARNING:  New scene without closing underscore!"
                    print "\tPossible runaway emphasis in line %i, file %s" % (lineno, repr(inf[1]))
                    in_ul = 0 # reset to good state
                    rtncode = 2 # report error to a Makefile, since
                    # this breaks TeX rules
                pass
            
            ful = line.find("_")
            while (ful >= 0):
                if in_ul == 0:
                    sub = "\\emph{"
                    in_ul = 1
                    pass
                else:
                    sub = "}"
                    in_ul = 0
                    pass
                line = line[:ful] + sub + line[ful+1:]
                ful = line.find("_")
                pass
            oldline = line
            line = re.sub("\[.*?\]", "", line)  # single line comments handled
            if line != oldline: comment_count += 1
            f_brack = line.find(cur_brack)
            if f_brack >= 0:
                if ignore == 0:
                    line = line[:f_brack]
                    ignore = 1
                    cur_brack = "]"
                    pass
                else:
                    line = line[f_brack+1:]
                    ignore = 0
                    cur_brack = "["
                    comment_count += 1
                    pass
                pass
            else:
                if ignore == 1:
                    line = ""
                    pass
                pass
            

            line = re.sub("\&", "\\&", line)
            line = re.sub("\%", "\\%", line)
            
            ouf.write(line)
            line = inf[0].readline()
            lineno = lineno + 1
            pass
        inf[0].close()
        if in_ul == 1:
            print "WARNING:  End of file without closing underscore!"
            print "\tPossible runaway emphasis in line %i, file %s" % (lineno, repr(inf[1]))
            in_ul = 0 # reset to good state
            rtncode = 2
            pass
        if comment_count > 0:
            plur = "s"
            if comment_count == 1: plur = ""
            print "Warning: %s comment%s removed from %s" % (comment_count, plur, inf[1])
        lastfile = inf[1]
        pass
    
    ouf.write("\\end{document}")
    ouf.close()
    sys.exit(rtncode)
    pass

