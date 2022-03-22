import gin
import os

@gin.configurable()
def runner(label, inner_class):
    print(f'Running {label}')
    obj = inner_class()
    print(obj.generate_stuff())
    print('finished')
    

if __name__ == '__main__':
    gins = [f for f in os.listdir() if f.endswith('.gin')]
    if len(gins) > 1 or len(gins) == 0:
        raise Exception('Should be exactly 1 gin in root')
    gin.parse_config_file(gins[0])
    runner()