from difflib import SequenceMatcher

inputStr = "sendcmd;a;fbrgbled r tb 1 2 3 4"
commands = ["ver", "bootloader", "pwmset", "vin", "vbat", "icharge", "batshort", "charge","vbatsw","sleep","sleeptime","bldcaccel","bldcspeed","bldcstop","bldcrpm","bldcdirrev","bldckp","bldcki","sma", "brake", "brakeseq", "brakedirrev", "led", "dbreset", "dbsleep", "dbtemp", "fbrgbled", "fblight","fbirled","fbtx","fbtxmsg","fbtxcount","fbtxled","fbrx", "fbrxcount", "fbrxflush","fbrxen","fbsleep","imuselect","imuinit","imuwrite","imuread", "imumotion","imuquat","imugravity","imugyros","bletx","blerx","blediscon","bleadv", "blemac","cp","ia","ltrack","tstfun"]

numSemi = 0;
for char in inputStr:
    if char == ";":
        numSemi +=1;
##if the string has two ; seperate
if numSemi ==2:
    part1 = inputStr.split(';')[0]
    part2 = inputStr.split(';')[1]
    part3 = inputStr.split(';')[2]
##compare first part to sendcmd return error
    m = SequenceMatcher(None, "sendcmd", part1)
    print "sendcmd matches " + str(m.ratio())
##compare second part to list of acceptable blocks, return error and guess
    
##look at first work in last part, compare to list, return error and guess
    recievedcmd = part3.split(" ")[0]
    match = 0
    bestMatch = "null"
    for word in commands:
        if SequenceMatcher(None, word, recievedcmd).ratio()> match:
            match = SequenceMatcher(None, word, recievedcmd).ratio()
            bestMatch = word
    print "command " + bestMatch + " matches " + str(match)

else:
    print "one of the semicolons was lost :("
    
        
