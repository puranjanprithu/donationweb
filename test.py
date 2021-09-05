
def checkThisNo(no):
    no= str(no)
    for i in no:
        if no.count(i)!=int(i):
            return False
    return True

d={1:1}
def beautifulNumber (N):
    # Write your code here
    last=list(d)[-1]
    if last >N:
        if list(d)[0]< N:
            for i in d:
                if i> N:
                    return i
    print(N,"...")
    while 1:
        N+=1
        if checkThisNo(N) :
            d[N]=N
            return N

T = int(input())
for _ in range(T):
    N = int(input())

    out_ = beautifulNumber(N)
    print (out_)



