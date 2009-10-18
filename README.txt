Simple readable random password generator in one Python file

This is a random password generator based on the most common
combinations of vowels and consonants in the English language. It
makes passwords that are simple to read and remember, but safe from
dictionary attacks. You can use this module in your program like this:

>>> from english_passwords import generate_password
>>> generate_password()
'cheedorth'
>>> generate_password(digits=2)
'gnorious23'

Known problems:
1. The algorithm may generate words that appear in an English dictionary.
2. The algorithm may generate profanities. To work around these problems,
   check the output against a word list and try again if necessary.
3. Without digits, the current version can generate only 140860
   different passwords. Adding digits is highly recommended, because
   it increases the search space for brute force attacks.

If you run this script on the command line without arguments, it will
generate 100 random passwords for you:

$ python english_passwords.py
steakent        mnefres         ghoptiod        ghonteps        veivetch
genthelms       rhymbest        glanswelps      nurthet         psystithms
smorbicts       toanioms        shackyst        candmeds        nibang
truenteeds      threarou        biablelp        whirious        cloublids
spouchatch      nuisew          ghappoils       sleckisc        wrisfarts
scettlisps      straintids      wridgerms       gnowips         weedlyths
prectlyl        fagults         sphersed        mnellals        sphetweipt
phansminds      postlyst        heybough        mnephirls       liallords
needeft         fronfrorks      zobjeck         criencies       splenlyl
joymerr         mnerbifts       streerus        brientlengths   flousipts
rhympail        gansior         funcherb        grairolls       oaninch
stoorilm        troubly         smarvirms       stricaught      ghamposts
vobtair         schechamps      pootnol         slinhept        clupom
stymbidth       foomirls        renthels        naireit         strurtoh
spheffi         fientlemns      steareir        culgength       shootnolt
wrojuch         glatyms         phrantlerbs     stoosough       chailief
chaffompts      schojers        reinstabs       psypyl          twitas
baudags         smorchilms      drossutt        peemuns         claudeal
roomul          spoilians       phrarblers      pimbild         pumains
loadioms        spoutrields     fleelouts       brexplairs      glonciews

This file is ready to use with common English letter combinations, but
you can also use it to generate combination dicts for other languages.
Then you can replace the dicts in this file with the new ones, and you
have a password generator for your own language, e.g. Klingon.

$ python english_passwords.py wordlist.txt 1000

The file wordlist.txt should contain one lowercase word on each line.
To make a simple wordlist for use with this script, download and
unpack SCOWL-6 and then run the following commands:

$ cd scowl-6/final
$ cat english-words.{10,20} | grep -v "'" | grep -v $'\xe9' > wordlist.txt
