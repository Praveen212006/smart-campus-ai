import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle


def train_model():

    # ---------------- LOAD DATASET ----------------

    data = pd.read_csv("admission.csv")


    # Show dataset information

    print("\nDataset Preview:")
    print(data.head())


    print("\nColumns:")
    print(data.columns)


    print("\nMissing Values:")
    print(data.isnull().sum())


    # Remove empty rows

    data = data.dropna()



    # ---------------- ENCODE TEXT DATA ----------------

    encoder = LabelEncoder()


    for column in data.select_dtypes(include="object").columns:

        data[column] = encoder.fit_transform(data[column])



    # ---------------- INPUT AND OUTPUT ----------------

    if "Admission_Status" not in data.columns:

        print("\nERROR: Admission_Status column not found")

        print("Available columns:")

        print(data.columns)

        return



    X = data.drop(
        "Admission_Status",
        axis=1
    )


    y = data["Admission_Status"]



    # ---------------- SPLIT DATA ----------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.2,

        random_state=42

    )



    # ---------------- TRAIN MODEL ----------------

    model = RandomForestClassifier(

        n_estimators=200,

        random_state=42

    )


    model.fit(

        X_train,

        y_train

    )



    # ---------------- TEST MODEL ----------------

    prediction = model.predict(X_test)


    accuracy = accuracy_score(

        y_test,

        prediction

    )


    print("\nModel Accuracy:")

    print(round(accuracy * 100,2), "%")



    # ---------------- SAVE MODEL ----------------

    pickle.dump(

        model,

        open(

            "admission_model.pkl",

            "wb"

        )

    )


    pickle.dump(

        X.columns,

        open(

            "columns.pkl",

            "wb"

        )

    )


    print("\nModel saved successfully!")




# ---------------- RUN ----------------

if __name__ == "__main__":

    train_model()