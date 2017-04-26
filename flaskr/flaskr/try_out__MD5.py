from MD5 import md5, md5_lea
s = md5('abc')
print s
#s = md5('abcde')
#print s
print md5_lea('a', s, 3)
# Out: 900150983cd24fb0d6963f7d28e17f72
#      9485808412f89f2b5693bb9f6afd16be

s = md5('wrx130713')
print s
