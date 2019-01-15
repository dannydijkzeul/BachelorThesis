with open("complete-fa-en.csv" , "w") as w:
    with open("filtered-fa-en.csv", "r") as r:
        line = r.readline()
        line = r.readline()
        while line:

            words = line.split(",")

            fa_word = words[1].rstrip()
            en_word = words[0].rstrip()

            if fa_word is not "":
                w.write(fa_word + "," + en_word + "\n")

            line = r.readline()
