with open("01-01.arc", "rb") as f1:
    with open("01-01_.arc", "rb") as f2:
        for i in range(2000):
            b1, b2 = f1.read(1), f2.read(1)
            if b1!=b2:
                input(f"{i}:   {b1}  {b2}")