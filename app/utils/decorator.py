#Zu den fortgeschritten Python-Konzepten gehören dekoratoren, generatoren, Context Manager,
#die dabei helfen, die saubern, effizienten Code zu schreiben, 

#Decorator
#Decorator ist eine Funktion, die andere Funktion modifiert ohne deren eigentlichen Code zu verändern

def log_function_call(fun):
    def wrapper():
        print(f"Calling {fun.__name__}")
        fun()
        print(f"Finished calling {fun.__name__}")
    return wrapper

if __name__ == "__main__":
    @log_function_call
    def hello():
        print("Hello, world!")
    hello()