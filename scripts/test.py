import time

t = time.time()
c = time.ctime(0)
print("Actual hour : ",int(t/(60*60)))
print("Actual day : ",int(t/(60*60*24)))
print(c)