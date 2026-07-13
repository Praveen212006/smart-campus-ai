import pickle
import pandas as pd


# Load trained model

model = pickle.load(
    open("admission_model.pkl", "rb")
)


# Load feature columns

columns = pickle.load(
    open("columns.pkl", "rb")
)



def predict_admission(student_data):

    try:

        # Convert input into dataframe

        input_data = pd.DataFrame(
            [student_data]
        )


        # Match training columns

        input_data = input_data.reindex(
            columns=columns,
            fill_value=0
        )


        # Prediction

        prediction = model.predict(
            input_data
        )


        # Probability

        probability = model.predict_proba(
            input_data
        )


        chance = round(
            max(probability[0]) * 100,
            2
        )


        # Result

        if prediction[0] == 1:

            result = "Admission Possible 🎉"

        else:

            result = "Admission Difficult"



        return result, chance



    except Exception as e:

        print("Prediction Error:", e)

        return "Prediction Failed", 0