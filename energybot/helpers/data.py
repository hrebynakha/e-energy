import pickle

FILE_NAME = "data.bin"



def load_data():
    with open(FILE_NAME, "rb") as fh:
        data = pickle.load(fh)
    return data



def save_data(data):
    with open(FILE_NAME, "wb") as fh:
        pickle.dump(data, fh)
