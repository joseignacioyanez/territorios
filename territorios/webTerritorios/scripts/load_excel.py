import pandas as pd
from yourapp.models import YourModel  # Import your Django model

def load_data():
    # Change 'your_file.xlsx' to the path of your Excel file
    df = pd.read_excel('your_file.xlsx')

    for index, row in df.iterrows():
        # Assuming YourModel has fields 'name', 'age', 'email', etc.
        obj = YourModel(
            name=row['name'],
            age=row['age'],
            email=row['email'],
            # Map other fields accordingly
        )
        obj.save()

if __name__ == '__main__':
    load_data()