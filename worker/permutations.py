# No external dependencies are required.

class Permutations:
    n = 0

    def __init__(self, n):
        """
        @param {*} n set cardinality
        """
        self.n = n

    def next(self, perm):
        n = self.n
        k = len(perm)

        i = k - 1
        while i >= 0 and perm[i] == n - 1:
            perm[i] = 0
            i -= 1

        if i < 0:
            # perm was the last permutation
            return False
        else:
            perm[i] += 1

        return True

    def at(self, index, k):
        perm = [0] * k
        n = self.n

        i = index
        j = k - 1
        while i:
            digit = i % n
            perm[j] = digit
            i = i // n  # Use floor division to mimic Math.floor in JavaScript
            j -= 1

        return perm
