class InnerClass2:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def generate_stuff(self):
        return 1e-2*self.a+1e-1*self.b+self.c