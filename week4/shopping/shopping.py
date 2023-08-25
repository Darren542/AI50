import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    with open(filename) as f:
            evidence_list = []
            labels_list = []
            month_names = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'June': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}
            contents = f.read().splitlines()
            first_row = True
            for row in contents:
                if first_row:
                    first_row = False
                    continue
                # Split the row up into its columns
                columns = row.split(',')
                # Int Columns
                columns[0] = int(columns[0])
                columns[2] = int(columns[2])
                columns[4] = int(columns[4])
                columns[11] = int(columns[11])
                columns[12] = int(columns[12])
                columns[13] = int(columns[13])
                columns[14] = int(columns[14])
                # Float Columns
                columns[1] = float(columns[1])
                columns[3] = float(columns[3])
                columns[5] = float(columns[5])
                columns[6] = float(columns[6])
                columns[7] = float(columns[7])
                columns[8] = float(columns[8])
                columns[9] = float(columns[9])
                # Month Column 10
                columns[10] = month_names[columns[10]]
                # Visitor Type
                columns[15] = 1 if columns[15] == 'Returning_Visitor' else 0
                # Weedend
                columns[16] = 1 if columns[16] == 'TRUE' else 0
                label = 1 if columns[17] == 'TRUE' else 0
                columns.pop()
                evidence_list.append(columns)
                labels_list.append(label)
            # print(evidence_list[0], labels_list[0])
            return tuple((evidence_list, labels_list))



def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # print('labels', labels)
    # print('predictions', predictions)
    totalOnes = 0
    correctOnes = 0
    totalZeros = 0
    correctZeros = 0
    for row in range(len(labels)):
        if labels[row] == 1:
            totalOnes += 1
            if predictions[row] == labels[row]:
                correctOnes += 1
        if labels[row] == 0:
            totalZeros += 1
            if predictions[row] == labels[row]:
                correctZeros += 1
    sensitivity = correctOnes / totalOnes if totalOnes != 0 else 0
    specificity = correctZeros / totalZeros if totalZeros != 0 else 0
    return tuple((sensitivity, specificity))


if __name__ == "__main__":
    main()
