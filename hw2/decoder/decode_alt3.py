#!/usr/bin/env python
import optparse
import sys
import models
import itertools, math
from collections import namedtuple, defaultdict

optparser = optparse.OptionParser()
optparser.add_option("-i", "--input", dest="input", default="data/input", help="File containing sentences to translate (default=data/input)")
optparser.add_option("-t", "--translation-model", dest="tm", default="data/tm", help="File containing translation model (default=data/tm)")
optparser.add_option("-l", "--language-model", dest="lm", default="data/lm", help="File containing ARPA-format language model (default=data/lm)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to decode (default=no limit)")
optparser.add_option("-k", "--translations-per-phrase", dest="k", default=1, type="int", help="Limit on number of translations to consider per phrase (default=1)")
optparser.add_option("-s", "--stack-size", dest="s", default=1, type="int", help="Maximum stack size (default=1)")
optparser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,  help="Verbose mode (default=off)")
opts = optparser.parse_args()[0]

tm = models.TM(opts.tm, opts.k)
lm = models.LM(opts.lm)
french = [tuple(line.strip().split()) for line in open(opts.input).readlines()[:opts.num_sents]]
def extract_english(h): 
  return "" if h.predecessor is None else "%s%s " % (extract_english(h.predecessor), h.phrase.english)

# tm should translate unknown words as-is with probability 1
for word in set(sum(french,())):
  if (word,) not in tm:
    tm[(word,)] = [models.phrase(word, 0.0)]

sys.stderr.write("Decoding %s...\n" % (opts.input,))
for f,french_sentence in enumerate(french):
  hypothesis = namedtuple("hypothesis", "logprob, lm_state, predecessor, phrase, bit_vec, remaining")
  bit_vec = defaultdict(bool)
  for word in french_sentence:
    bit_vec[word] = False
  initial_hypothesis = hypothesis(0.0, lm.begin(), None, None, bit_vec, len(french_sentence))
  hypotheses = [{} for _ in french_sentence] + [{}]
  hypotheses[0][''] = initial_hypothesis
  translated = False
  phrase_len = 6
  prev_len = len(hypotheses[0])

  while not translated:
    false_alarm = False
    for current_hypothesis in sorted(hypotheses[0].itervalues(),key = lambda h: (h.remaining,-h.logprob))[:opts.s]:
      for i in xrange(1, phrase_len+1):
        s = tuple()
        for j, word in enumerate(french_sentence):
          if len(s) >= phrase_len:
            break
          if not current_hypothesis.bit_vec[french_sentence[j]]:
            s += (french_sentence[j],)
        counter = 0
        for perm in itertools.permutations(s[0:i]):
          if perm in tm:
            remaining = current_hypothesis.remaining
            remaining -= len(perm)
            for phrase in tm[perm]:
              logprob = current_hypothesis.logprob + phrase.logprob
              current_lm_state = current_hypothesis.lm_state
              for word in phrase.english.split():
                (current_lm_state, word_logprob) = lm.score(current_lm_state, word)
                logprob += word_logprob
              logprob += lm.end(current_lm_state)
              current_bit_vec = defaultdict(bool)
              for word in french_sentence:
                current_bit_vec[word] = current_hypothesis.bit_vec[word]
              
              for word in perm:
                current_bit_vec[word] = True
              #sys.stderr.write(str(phrase)+'\n')
              #pause = raw_input()
              new_hypothesis = hypothesis(logprob,
                                          current_lm_state,
                                          current_hypothesis,
                                          phrase,
                                          current_bit_vec,
                                          remaining)
              if extract_english(new_hypothesis) not in hypotheses[0] or hypotheses[0][extract_english(new_hypothesis)].logprob < logprob:
                hypotheses[0][extract_english(new_hypothesis)] = new_hypothesis
          else:
            counter+=1
          
        if counter == i and len(s)>0:
          false_alarm = True

    sys.stderr.write("top contenders:\n")
    for hyp in sorted(hypotheses[0].itervalues(), key = lambda h: (h.remaining,-h.logprob))[:20]:
      sys.stderr.write(extract_english(hyp)+ ' --------------- log prob: %6.6f' % hyp.logprob + '\n')
    sys.stderr.write("current: %i prev: %i\n" % (len(hypotheses[0]),prev_len))
    sys.stderr.write('\n--------------------\n')
    #pause = raw_input()    

    if len(hypotheses[0]) == prev_len:
      translated = True
    prev_len = len(hypotheses[0])

  
  for hyp in hypotheses[0].itervalues():
    validation = True
    for word in french_sentence:
      if not hyp.bit_vec[word]:
        validation = False
    if not validation:
      logprob = float('-inf')
      new_hypothesis = hypothesis(logprob,
                                  hyp.lm_state,
                                  hyp.predecessor,
                                  hyp.phrase,
                                  hyp.bit_vec,
                                  0)
      hypotheses[0][extract_english(hyp)] = new_hypothesis
  
  #for hyp in sorted(hypotheses[0].itervalues(), key = lambda h: -h.logprob)[:opts.s]:
  #  sys.stderr.write(extract_english(hyp) + '\n')

  winner = max(hypotheses[0].itervalues(), key = lambda h: h.logprob)
  sys.stderr.write(str(winner.bit_vec)+'\n')
  sys.stderr.write("winner!: " + extract_english(winner) + '\n')
  print extract_english(winner)
  #pause = raw_input()