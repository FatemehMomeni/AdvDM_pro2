from sklearn import preprocessing
import matplotlib.pyplot as plt
import statistics


class Exploratory:
    frequencies = dict()  # key = item, value = support_count
    transaction_length = list()

    def __init__(self, dataset):
        self.items_frequency(dataset)
        self.histogram(dataset)
        self.scatter()
        self.box()
        self.results()

    def items_frequency(self, dataset):
        for transaction in dataset:
            for item in transaction:
                if item in self.frequencies:
                    self.frequencies[item] += 1
                else:
                    self.frequencies[item] = 1
        self.frequencies = dict(sorted(self.frequencies.items(), key=lambda x: x[1]))

    def histogram(self, dataset):
        for transaction in dataset:
            self.transaction_length.append(len(transaction))
        plt.figure(figsize=(10, 6))
        plt.hist(self.transaction_length)
        plt.xlabel('transactions')
        plt.ylabel('numer of items')
        plt.title('Histogram plot\n')
        plt.show()

    def scatter(self):
        x = self.frequencies.keys()
        y = self.frequencies.values()
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y)
        plt.xlabel('transactions')
        plt.ylabel('numer of items')
        plt.title('Scatter plot\n')
        plt.show()

    def box(self):
        plt.figure(figsize=(10, 6))
        plt.boxplot(self.frequencies.values())
        plt.title('Box plot\n')
        plt.show()

    def results(self):
        print('The item with the most sales:')
        for key in self.frequencies:
            if self.frequencies[key] == self.frequencies[list(self.frequencies.keys())[-1]]:
                print(key, '   ', end='')

        print('\n\nThe item with the lowest sales:')
        for key in self.frequencies:
            if self.frequencies[key] == self.frequencies[list(self.frequencies.keys())[0]]:
                print(key, '   ', end='')

        print('\n\nAverage number of sales related to each item:')
        print(statistics.mean(self.transaction_length))
        print('\nMedian number of sales related to each item:')
        print(statistics.median(self.transaction_length))

        print('\nAverage number of items in transactions:')
        print(statistics.mean(self.frequencies.values()))
        print('\nMedian number of items in transactions:')
        print(statistics.median(self.frequencies.values()))
