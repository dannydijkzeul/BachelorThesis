import re
with open("filtered-fa-en.csv" , "w") as w:
    with open("fa-en.txt", "r") as r:
        line = r.readline()
        count = 0
        while line:

            words = line.split("~")
            fa_word = words[1].strip("\n")
            en_word = words[0]

            if "span" not in fa_word and "<i>" not in fa_word and "<div" not in fa_word:
                w.write(en_word.strip("[") + "," + fa_word.strip("]").split(",")[0] + "\n")
                count += 1
            elif '<span class="dictionary_number_bold">1</span> ':
                fa_word = fa_word.replace('<span class=\"dictionary_number_bold\">1</span> ','' ).replace(", ", " ")
                fa_word = re.sub(r'<i>.*<\/i> ', "", fa_word)
                w.write(en_word.strip("[") + "," + fa_word.split(" ")[0].strip("]") + "\n")
                count += 1
            line = r.readline()

        print count
