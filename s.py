''' 
procol scheme): communication topology of protocols, along with transformations on these orders '''


def msg_replace(tups, m, new):
    out = []
    for tup in tups:
        (t1, t2, m) = tup
        mp = [x if x != m else new for x in m]
        out += [(t1, t2, mp)]
    return out

def m_s(x, m1, m2):
    if x == m1:
        return m2
    else:
        return m1

def msg_swap(tups, m1, m2):
    out = []
    for tup in tups:
        (t1, t2, m) = tup
        mp = [x if x != m1 and x != m2 else m_s(x, m1, m2) for x in m]
        out += [(t1, t2, mp)]
    return out


def id_replace(tups, p, new):
    out = []
    for tup in tups:
        (t1, t2, m) = tup
        if t1 == p:
            t1 = new
        if t2 == p:
            t2 = new
        if t1 != t2:
            out += [(t1, t2, m)]
    return out

def id_join(tups, p1, p2, new):
    out = []
    for tup in tups:
        (t1, t2, m) = tup
        if t1 in [p1, p2]:
            t1 = new
        if t2 in [p1, p2]:
            t2 = new
        if t1 != t2:
            out += [(t1, t2, m)]
    return out

def id_swap(tups, a, b):
    out = []
    for tup in tups:
        (t1, t2, m) = tup
        if t1 == a:
            t1 = b
        elif t1 == b:
            t1 = a
        if t2 == a:
            t2 = b
        elif t2 == b:
            t2 = a
        out += [(t1, t2, m)]
    return out

def msg_flatten(m):
    s = ""
    for a in m:
        s += str(a) + " "
    return s[:-1]

class PScheme:
    def __init__(self, tups):
        self.parties = set([t[0] for t in tups]).union(set([t[1] for t in tups]))
        self.scheme = tups
    

    def id_join(self, p1, p2, new):
        if p1 not in self.parties or p2 not in self.parties:
            print("party not found")
            return
        return PScheme(id_join(self.scheme, p1, p2, new))

    def id_swap(self, a, b):
        if a not in self.parties or b not in self.parties:
            print("party not found")
            return
        return PScheme(id_swap(self.scheme, a, b))

    def msg_swap(self, a, b):
        return PScheme(msg_swap(self.scheme, a, b))

    def reorder(self, i, j):
        self.scheme[i], self.scheme[j] = self.scheme[j], self.scheme[i]
        return self

    def __str__(self):
        s = ""
        max_len = max([len(n) for n in self.parties])
        templ = "{0:>%d} --> {1:>%d} : {2}\n" % (max_len, max_len)
        for tup in self.scheme:
            s += templ.format(tup[0], tup[1], msg_flatten(tup[2]))
        return s

Env = "Env"
Alice = "Alice"
Bob = "Bob"
F_RPS = "F_RPS"

F_comm = "F_Comm"
Fc1 = "F_Comm_1"
Fc2 = "F_Comm_2"
F_commplus = "F_Comm + F_Comm"
x1 = 'x1'
x2 = 'x2'
def Input(a):
    return ['Input', a]


''' protocol model:
    1. env supply inputs in some order to parties
    2. protocol runs. parties activated automatically
    3. parties return their input to env, in same order as 1)
'''



ideal_scheme = PScheme([
    # alice input
    #(Env, Alice, Input(x1)),
    # bob input
    #(Env, Bob, Input(x2)),
    # protocol start
    #(F_RPS, Alice, ['Notify']),
    (Alice, F_RPS, ['Play', x1]),
    #(F_RPS, Bob, ['Notify']),
    (Bob, F_RPS, ['Play', x2]),
    # alice check
    (F_RPS, Alice, ['Notify']),
    (Alice, F_RPS, ["Query"]),
    (F_RPS, Alice, ["Leak", x2]),
    # bob check
    (F_RPS, Bob, ['Notify']),
    (Bob, F_RPS, ["Query"]),
    (F_RPS, Bob, ['Leak', x1]),
    # output return
    #(Alice, Env, ['Output']),
    #(Bob, Env, ['Output'])
    ])

real_scheme_fc = PScheme([
    # alice input
    #(Env, Alice, Input(x1)),
    # bob input
    #(Env, Bob, Input(x2)),
    # protocol start
    # alice commit
    (Alice, Fc1, ['Commit', x1]),
    # commit notify bob
    (Fc1, Bob, ['Committed']),
    # bob commit
    (Bob, Fc2, ['Commit', x2]),
    # commit notify alice
    (Fc2, Alice, ['Committed']),
    # alice reveal
    (Alice, Fc1, ['Reveal']),
    (Fc1, Bob, ['Leak', x1]),
    (Bob, Fc2, ['Reveal']),
    (Fc2, Alice, ['Leak', x2]),
    #(Alice, Env, ['Output']),
    #(Bob, Env, ['Output'])
    ])

real_scheme = PScheme([
    # alice input
    #(Env, Alice, ('Input', 'x1')),
    # bob input
    #(Env, Bob, ('Input'),
    # protocol start
    # alice commit
    (Alice, Bob, ['Hash', x1]),
    # commit notify bob
    (Bob, Alice, ['Hash', x2]),
    (Alice, Bob, ['Leak', x1]),
    (Bob, Alice, ['Leak', x2]),
    #(Alice, Env, ['Output']),
    #(Bob, Env, ['Output'])
    ])

print("Real swap: ")
print(real_scheme_fc.id_join(Fc1, Fc2, 'F_RPS').id_swap(Alice, Bob).msg_swap(x1, x2))

print("Ideal:")
print(ideal_scheme)


''' if we modify F_RPS to modify the _other_ party, ideal is nearly exact the same as real except for activations. '''


''' swap:

    (a,b, m1)
    (c,d, m2)

    can swap to

    (c,d, m2)
    (a,b, m1)

    if:
        m2 is indepenent of (a, b, m1)
        and activations don't give away information
'''

