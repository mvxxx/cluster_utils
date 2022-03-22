import gin

def configure_job(inner_class):
    return gin.external_configurable(
        inner_class, module='inners'
    )

from inners import inner_file
from inners import inner_file2

InnerClass = configure_job(inner_file.InnerClass)
InnerClass2 = configure_job(inner_file2.InnerClass2)
