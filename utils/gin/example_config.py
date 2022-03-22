configs = [
f'''
import inners

runner.label = 'test-run'
runner.inner_class = @inners.InnerClass

# Parameters for InnerClass2:
# ==============================================================================
InnerClass2.a = 7
InnerClass2.b = 13
InnerClass2.c = {v}


# Parameters for InnerClass:
# ==============================================================================
InnerClass.a = 11
InnerClass.b = 17
InnerClass.c = 31
''' for v in [10, 100, 1000]]
