from optparse import OptionParser
import sys
import math
import EDA


dataset = list()  # each element of this list is a transaction


class Arules:
    large_item_sets = dict()  # key = number of large item set, value = large item set
    candidate_item_sets = list()
    rules = list(list())

    def __init__(self, min_support, min_confidence):
        self.get_frequent_itme_sets(min_support)
        self.get_arules(min_confidence)
        self.print_results()

    def get_frequent_itme_sets(self, min_support):
        self.large_item_sets[1] = self.support_count(1, min_support, False, None)
        k = 2
        while self.large_item_sets[k-1]:
            self.apriori_gen(k)
            self.large_item_sets[k] = self.support_count(k, min_support, False, None)
            k += 1
            self.candidate_item_sets.clear()

    def support_count(self, k, min_support, gen_rule, lhs):
        items_frequency = dict()  # key = item, value = support_count
        for transaction in dataset:
            if k == 1:
                for item in transaction:
                    if item in items_frequency:
                        items_frequency[item] += 1
                    else:
                        items_frequency[item] = 1
            elif k == -1:
                single = lhs.split(',')
                if all(i in transaction for i in single):
                    if lhs in items_frequency:
                        items_frequency[lhs] += 1
                    else:
                        items_frequency[lhs] = 1
            else:
                for item in self.candidate_item_sets:
                    item_set = item.split(',')
                    if all(i in transaction for i in item_set):
                        if item in items_frequency:
                            items_frequency[item] += 1
                        else:
                            items_frequency[item] = 1

        if not gen_rule:
            temp = items_frequency.copy()
            items_frequency.clear()
            for i in sorted(temp.keys()):
                items_frequency[i] = temp[i]

            items_frequency = self.min_support_threshold(items_frequency, min_support)

        return items_frequency

    def min_support_threshold(self, items_frequency, min_support):
        for item in items_frequency.keys():
            item_support = items_frequency[item] / len(dataset)
            if item_support < min_support:
                items_frequency[item] = -1
        items_frequency = {key: value for key, value in items_frequency.items() if value != -1}
        return items_frequency

    def apriori_gen(self, k):
        k_1Itemsets = list(self.large_item_sets[k-1].keys())
        k_1Itemsets.pop()
        for i in k_1Itemsets:
            i_prin = i.split(',')
            j_Itemsets = list(self.large_item_sets[k-1].keys())
            m = 0
            while j_Itemsets[m] != i:
                j_Itemsets.pop(m)
            j_Itemsets.pop(0)

            for j in j_Itemsets:
                j_prin = j.split(',')
                k_1PreviuosItems = True
                for n in range(0, (k-1+k-2)-2, 2):  # (k-1+k-2)=item set length
                    if i_prin[n] != j_prin[n]:
                        k_1PreviuosItems = False
                        break
                if k_1PreviuosItems and i_prin[-1] < j_prin[-1]:
                    c = self.join_item_sets(i, j)
                    infrequent = self.has_infrequent_subset(c)
                    if not infrequent:
                        self.candidate_item_sets.append(c)

    def join_item_sets(self, l1, l2):
        l1 = l1.split(',')
        l2 = l2.split(',')
        duplicate_c = list(set(l1+l2))
        duplicate_c.sort()
        c = duplicate_c[0]
        for item in range(1, len(duplicate_c)):
            c = c + ',' + duplicate_c[item]
        return c

    def has_infrequent_subset(self, c):
        a = c.split(',')
        k = math.ceil(len(a)/2) + 1
        counter = 0
        for frequent in self.large_item_sets[k-1].keys():
            if all(x in c for x in frequent):
                counter += 1
        if k == counter:
            return False
        else:
            return True

    def get_arules(self, min_confidence):
        frequent_larges = list(self.large_item_sets.keys())
        large_n = frequent_larges[-1]
        for subset_num in range(2, large_n):
            for itemset in self.large_item_sets[subset_num]:
                items = itemset.split(',')
                for rhs in items:
                    lhs = itemset.replace(rhs, '')

                    if lhs[0] == ',':
                        lhs = lhs[1:]
                    elif lhs[-1] == ',':
                        lhs = lhs[:-1]
                    else:
                        extra = list()
                        for ch in range(1, len(lhs)):
                            if lhs[ch] == ',' and lhs[ch+1] == ',':
                                extra.append(ch)
                        for i in extra:
                            lhs = lhs[:i] + lhs[i+1:]

                    # rule: s -> i-s
                    support_count_i = self.large_item_sets[subset_num][itemset]
                    support_count_s = self.support_count(-1, 0, True, lhs)
                    support_count_lhs = support_count_s[list(support_count_s.keys())[0]]
                    confidence = support_count_i / support_count_lhs
                    if confidence >= min_confidence:
                        total = len(dataset)
                        p_l_r = support_count_i / total
                        p_l = support_count_lhs / total
                        p_r = self.large_item_sets[1][rhs] / total
                        lift = p_l_r / (p_l * p_r)
                        if lift > 1:
                            self.rules.append([lhs, rhs, lift, confidence, support_count_i/len(dataset)])
        sorted(self.rules, key=lambda x: (x[2], x[3], x[4]))

    def print_results(self):
        larges = list(self.large_item_sets.keys())
        larges.pop()
        print('------------------------- Large Itemsets -------------------------')
        for i in larges:
            print('\n', 'Large Itemset', i)
            for j in self.large_item_sets[i]:
                print(j, '\t', self.large_item_sets[i][j])

        print('\n------------------------- Association Rules -------------------------')
        for i in self.rules:
            print(i[0], '=>', i[1], '\tlift: ', i[2], 'confidence: ', i[3], 'support: ', i[4])


def read_transactions(transactions):
    with open(transactions, "r") as file_iter:
        for line in file_iter:
            line = line.strip().rstrip(",")
            dataset.append(line.split(","))


if __name__ == '__main__':
    optparser = OptionParser()
    optparser.add_option("-f", "--inputFile", dest="input", help="filename containing csv", default=None)
    optparser.add_option("-s", "--minSupport", dest="minS", help="minimum support value", default=0.5, type="float", )
    optparser.add_option("-c", "--minConfidence", dest="minC", help="minimum confidence value", default=0.5, type="float", )
    optparser.add_option("-q", "--questionNum", dest="num", help="number of question", default=None, type="int", )
    (options, args) = optparser.parse_args()
    inputFile = None
    if options.input is None:
        inputFile = sys.stdin
    elif options.input is not None:
        inputFile = options.input
    else:
        print("No dataset filename specified, system with exit\n")
        sys.exit("System will exit")

    read_transactions(inputFile)

    if options.num == 1:
        eda = EDA.Exploratory(dataset)
    else:
        minSupport = options.minS
        minConfidence = options.minC
        a_rules = Arules(options.minS, options.minC)
