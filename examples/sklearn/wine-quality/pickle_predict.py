
""" Serve predictions by unpickling model artifact file. """

from __future__ import print_function
import sys
import pickle
import predict_util

if __name__ == "__main__":
    if len(sys.argv) < 1:
        println("ERROR: Expecting PICKLE_FILE PREDICTION_FILE")
        sys.exit(1)
    pickle_path = sys.argv[1]
    data_path = sys.argv[2] if len(sys.argv) > 2 else "../../data/wine-quality/wine-quality-red.csv"
    print("pickle_path:",pickle_path)
    print("data_path:",data_path)

    with open(pickle_path, 'rb') as f:
        model = pickle.load(f)
    print("model:",model)
    print("model type:",type(model))
    predict_util.run_predictions(model,data_path)
