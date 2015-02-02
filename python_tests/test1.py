#! /usr/bin/python
from numpy import *
print "Hello world"
x = 1
if x==1:
    print x+5.3
b = [1,2,3,4]

print b[0]

c = 2 ** 3
print "Hello %6.6f" % c ** (1/float(2))
print len(b)
count = 0
while count < 10:
    print count
    count+=1;


a = arange(15).reshape(3,5)
print a.shape
b = array([ [1,1.5,2,6] ,  [1,1.5,2,6] ])
print b
