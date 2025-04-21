from hashlib import md5
from time import sleep

from permutations import Permutations


# HashBruteForce class translation with exact preservation of structure and functionality.
class HashBruteForce:

    def crackHash(self, obj, trackProgress):
        # Extracting parameters from the input dictionary to preserve names exactly as in the original code
        hash = obj["hash"]
        alphabet = obj["alphabet"]
        start = obj["start"]
        count = obj["count"]

        n = len(alphabet)
        permutation = Permutations(n)

        k = 1
        threshold = self._permutationsCount(n, k)
        while start > threshold:
            k += 1
            threshold += self._permutationsCount(n, k)

        result = []
        index = start - (threshold - self._permutationsCount(n, k))
        p = permutation.at(index, k)
        while count > 0:
            word = self._permutationToWord(p, alphabet)
            h = md5(word.encode("utf-8")).hexdigest()
            if h == hash:
                result.append(word)

            count -= 1
            trackProgress()
            if not permutation.next(p):
                k += 1
                p = permutation.at(0, k)

            if count % 10 == 0:
                sleep(0)

        return result

    def _permutationsCount(self, n, k):
        return n ** k

    def _permutationToWord(self, perm, alphabet):
        chars = [alphabet[x] for x in perm]
        return "".join(chars)

