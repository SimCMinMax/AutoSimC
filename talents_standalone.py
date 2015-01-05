file=open('talents.simc','w')
l=[0,0,0,0,0,0,0]

### Comment or uncomment and indent for & l[x] line as you need, this example is for a dps monk

#for a in range(1,4):
    #l[0]=a
for b in range(1,4):
    l[1]=b
    for c in range(1,4):
        l[2]=c
            #for d in range(1,4):
                #l[3]=d
                #for e in range(1,4):
                    #l[4]=e
        for f in range(1,4):
            l[5]=f
            for g in range(1,4):
                l[6]=g
                file.write("copy=%i%i%i%i%i%i%i\n" % (l[0],l[1],l[2],l[3],l[4],l[5],l[6]))
                file.write("talents=%i%i%i%i%i%i%i\n\n" % (l[0],l[1],l[2],l[3],l[4],l[5],l[6]))
                
file.close