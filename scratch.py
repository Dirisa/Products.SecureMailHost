a = [1,2,[3,4],[5,[6,7,8],7],8]

def flatten(*seq):
    results = []
    for item in seq:
        if type(item) in seq_types: results += flatten(*item)
        else: results.append(item)
    return results

seq_types = (type(()), type([]))
