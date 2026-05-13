import pandas as pd

def load_invoice_data(file_path):
    df = pd.read_csv(file_path)

    # Convert due_date column to datetime
    df["due_date"] = pd.to_datetime(df["due_date"])

    return df