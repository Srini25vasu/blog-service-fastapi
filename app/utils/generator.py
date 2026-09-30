#Ein Generator verwendet 'yied', um jeweils einen Wert zurückzugeben.
# Dies spart Arbeitspeicher des Computers, da die Werte gleichzeitig
# im Arbeitsspeicher abgelegt werden.

def count_num(max):
    count = 1
    while count <= max:
        yield count
        count += 1
        
if __name__ == "__main__":
    for num in count_num(10):
        print(num)