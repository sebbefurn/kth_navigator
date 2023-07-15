import time

def tictoc(func):
    def wrapper():
        t1 = time.time()
        func()
        ans = time.time() - t1
        print(f"The function took {ans} seconds to run")
    return wrapper

@tictoc
def hello():
    print("HELLO WORLD")
    time.sleep(2)

hello()