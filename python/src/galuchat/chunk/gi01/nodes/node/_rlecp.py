from typing import List, Tuple


def rlecp(data_iter)->Tuple[List[int],List[int]]:
    count = 1
    clist=[]
    plist=[]
    prev = next(data_iter)
    for current in data_iter:
        if prev == current:
            count += 1
        else:
            clist.append(count)
            plist.append(prev)
            count = 1
        prev = current
    clist.append(count)
    plist.append(prev)
    return clist,plist


