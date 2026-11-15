import requests
import pandas as pd
url = "https://openlibrary.org/search.json?q=Rip+it+Up+and+Start+Again"
headers = {
    "User-Agent": "MyAppName/1.0 (myemail@example.com)"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)  # Convert the JSON data to a DataFrame
    #print(df.iloc[0])  # Print the first book found in the search results
    print(df.head()["docs"][2])  # Print the first few rows of the DataFrame
else:   
    print(f"Request failed with status code: {response.status_code}")
    

    
    