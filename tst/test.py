for i in range(1,10):
    try:
        raise Exception("something went wrong") 
    except:
        print("#2")
        continue
        pass