A = [2,2,2,2,1]


def solution(A):
    adjacent_flag = False
    distance = []
    for p in range(len(A)):
        for q in range(p+1,len(A)):
            val_p, val_q = A[p], A[q]
            if val_p != val_q: # Checks 1st condition of A[P] != A[P}
                if val_p < val_q:
                    min, max = val_p, val_q
                elif val_p > val_q:
                    min, max = val_q, val_p # helpful in iterating from lowest to highest

                val_list = []
                for val_range in range(min+1,max): # Make a list of all integers present b/w 2 value ranges
                    val_list.append(val_range)
                flag = True
                for value in val_list: # Iterate over the list to check if it is present in array A
                    if value in A:
                        flag = False # even on single occurrence its discarded
                if flag:
                    adjacent_flag = True # if even one adjacent pair occurred; dont return -1
                    distance.append(abs(p-q))
                    print(p, q, "----", min, max)
                    print(flag)
                    print("_" * 50)
    if adjacent_flag:
        distance.sort()
        min_dist = distance[0]
        return min_dist
    else:
        return -1


result = solution(A)
print("Minimum Distance: ",result)

