print("BEFORE")
L=[]
count = 0
while 1:
    response = input()
    count += 1
    L.append(response)
    print((response+ " WORKING ", count,L).split())
