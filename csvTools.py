import csv
def getCsvFromDict(dictArray, columnNames, csvFilename="test.csv"):
    with open(csvFilename, 'w', newline='') as csvfile:
        if (len(dictArray) == 0):
            return

        writer = csv.DictWriter(csvfile,fieldnames=columnNames, extrasaction='ignore')
        writer.writeheader()
        for d in dictArray:
            writer.writerow(d)