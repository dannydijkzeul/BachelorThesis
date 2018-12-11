import os

list = [5000, 10000, 25000, 50000, 100000]
for i in list:
  os.system("python2 unsupervised.py --exp_path data/results/ --exp_name alignments --src_emb data/modelFaroeseScrapedCleaned.vec --tgt_emb data/modelEnglishCleaned.vec  --dis_most_frequent 0 --epoch_size 500000 --exp_id tensorboard_lr_05_most_frequent_0_max_vocab_" + str(i) + " --max_vocab " + str(i) + " --dis_optimizer sgd,lr=0.05 --map_optimizer sgd,lr=0.05")
