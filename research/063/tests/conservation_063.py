# Vektor-063 return-link capacity bound
def capacity(p, shared):
    return 1/(2+p) if shared else 1/(1+p)
for p in (0,0.1,0.4):
    assert capacity(p, True) < capacity(p, False)
print("PASS Vektor-063 conservation")
