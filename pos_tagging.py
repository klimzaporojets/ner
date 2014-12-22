import nltk 

tokens = nltk.word_tokenize("All are welcome , joe included.")
#nltk.word_tokenize("The Wolves to host the Lions for game time")

tagged_tokens = nltk.pos_tag(tokens)

print tagged_tokens

#The Wolves to host the Lions for game time 