#!/bin/sh
python schattie_v2.py
crfsuite learn -m mymodel -p c1=0 -p c2=0 train_and_dev.feats
crfsuite tag -m mymodel test_withlabels.feats > predtags
python tageval.py test_withlabels.txt predtags