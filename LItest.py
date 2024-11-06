from linkedin_api import Linkedin
import pandas as pd

# Authenticate using any LinkedIn account credentials
api = Linkedin('tylerhaney@outlook.com', 'Four097khan')

# Fetch connections
connections = api.get_connections()

# Extract required fields
data = []
for connection in connections:
    first_name = connection.get('firstName', '')
    last_name = connection.get('lastName', '')
    company = connection.get('companyName', '')
    position = connection.get('title', '')
    data.append([first_name, last_name, company, position])

# Create a DataFrame and save to Excel
df = pd.DataFrame(data, columns=['First Name', 'Last Name', 'Company', 'Position'])
df.to_excel('LinkedIn_Connections.xlsx', index=False)
