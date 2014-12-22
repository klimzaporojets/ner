# Updated 2014-12-01
import sys
import tageval
#from tageval import  convert_bio_to_spans

def getTag(line):
     if line.strip():
          fields = line.rstrip().split("-")
          return fields[0]
     else:
          return "O"
    
def main():
    owplFile = sys.argv[1]
    print "Id,Prediction"
    sys.stdout.write("0,")
    toktags = tageval.read_tags_file(owplFile)
    
    start = 0
    for tags in toktags:
         spans = tageval.convert_bio_to_spans(tags)
         for c in spans:
              sys.stdout.write(" %s-%d-%d" % (c[0],c[1] + start,c[2] + start))
         start = start + len(tags)
    sys.stdout.write("\n")    



if __name__ == "__main__":
    main()
