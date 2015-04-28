#!/usr/bin/env python
#script to align parallel senteces from Wikipedia articvle incorporating the alignment history


from __future__ import division
import optparse
import sys
import string

optparser = optparse.OptionParser()
optparser.add_option("-d", "--data", dest="train", default="data-train/", help="Data filename prefix (default=data)")
optparser.add_option("-e", "--english", dest="english", default="orig.enu.snt", help="Suffix of English filename")
optparser.add_option("-s", "--spanish", dest="spanish", default="orig.esn.snt", help="Suffix of French filename")
optparser.add_option("-o", "--output", dest="output", default="output", help="Prefix of filename to output to")
optparser.add_option("-r", "--dict", dest="esdict", default="./data-train/dict.es", help="Spanish to English Dictionary")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.2, type="float", help="Threshold (default=0.5)")
optparser.add_option("-p", "--PROPER_W", dest="PROPER_W", default=2.5, type="float", help="Proper Noun Weight (default=10.0)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
optparser.add_option("-w", "--windowsize", dest="win_size", default=200, type="int", help="Window size")
optparser.add_option("-l", "--stoplist", dest="stop_file", default="stopwords.txt", help="List of stop words")
optparser.add_option("-k", "--length_ratio", dest="length_ratio", default=1.18, type="float",help="ratio of len(spanish) to len(english)")

(opts, _) = optparser.parse_args()
s_data = "%s%s" % (opts.train, opts.spanish)
e_data = "%s%s" % (opts.train, opts.english)

#######################
## open stop words file
#######################
stopwords = set([word.strip() for word in open(opts.stop_file)])
punct = string.punctuation
for p in punct:
    stopwords.add(p)
additions = ['-LRB-', '-RRB-', '\'\'', '``', '...']
for p in additions:
    stopwords.add(p)

#####################################
## open spanish to english dictionary
#####################################
es_lists = [line.strip().split() for line in open(opts.esdict)]
# make the dictionary
es_map = {}
for es_line in es_lists:
    es_map[es_line[0]] = es_line[1:]
PROPER_W = opts.PROPER_W
konstant_length_ratio = opts.length_ratio

#mathcing
e_hist = [] #mathcing history variables to consider previous matches as an idication of future performance
s_hist = []
hist_const = 1


e_output = []
s_output = []

###############
## read in data
###############
def read_pages ( fn ):
  with open(fn,'r') as f:
    document = []
    line_number = 0
    for line in f:
      if len(line.strip()) == 0:
        yield (" ".join(document[0][0]), document[1:])
        line_number = 0
        document = []
        continue
      else:
        document.append((line.strip().split(), line_number))
      line_number += 1

document_pairs = [(de, ds) for (de, ds) in zip(read_pages(e_data), read_pages(s_data))]

for (e_data, s_data) in document_pairs:
	# put each english sentence in file into a list
	#e_sents = [english.strip() for english in open(e_data) if len(english.strip()) > 0][:opts.num_sents]
	(title_e, document_e) = e_data

	# put each spanish sentence from file into a list
	#s_sents = [spanish.strip() for spanish in open(s_data) if len(spanish.strip()) > 0][:opts.num_sents]
	(title_s, document_s) = s_data

	for (e_list, eindex) in document_e:
	#for eindex, e in enumerate(e_sents):
		if eindex % 50 == 0:
			sys.stderr.write('.')
		best_score = 0
		best_s = ""
		#e_list = e.split()
		e_len = len(e_list)
		e_bit_vec = [0]*e_len
		start = max(0, eindex - opts.win_size)
		#end = min(len(s_sents), eindex + opts.win_size)
		end = min(len(document_s), eindex + opts.win_size)
		aligned = False
		for (s,sindex) in document_s:
		#for sindex, s in enumerate(s_sents[start:end]):
			lenSpan_to_lenEng = float(len(s))/e_len
			lengthDiffFromTarget = abs(konstant_length_ratio - lenSpan_to_lenEng)

			sindex += start
			if sindex not in s_hist:
				count_overlap = 0
				count_same = 0
				for s_word in s:
				#for s_word in s.split():
					translated = False
					if s_word.lower() in es_map:
						translations = es_map[s_word.lower()]
						for k, e_word in enumerate(e_list):
							if e_word.lower() in translations and not translated and e_bit_vec[k] == 0 and e_word not in stopwords:
								translated = True
								e_bit_vec[k] = 1
								count_overlap = count_overlap + 1
					else:
						for k, word in enumerate(e_list):
							if not e_bit_vec[k] and word == s_word and not translated and word not in stopwords:
								#sys.stderr.write(word + '   ' + s_word + '\n')
								count_same += 1
								translated = True
								e_bit_vec[k] = 1
				score = hist_const*((count_overlap+PROPER_W*count_same) / e_len)
				score *= (1-lengthDiffFromTarget)
				
				#append each sentence if above thresh
				if score > best_score:
					#best_s = s
					best_s = ' '.join(s)
					best_sindex = sindex
					best_score = score
		if best_score > opts.threshold:
			#e_output.append(e)
			e_output.append(title_e)
			e_hist += [eindex]
			#s_output.append(best_s)
			s_output.append(title_s)
			s_hist += [best_sindex]

	for e,s,e_idx, s_idx in zip(e_output, s_output, e_hist, s_hist):
		print "\t".join([s,e,str(s_idx-1),str(e_idx-1)])
	#e_output = []
	#s_output = []
	#e_hist = []
	#s_hist = []
