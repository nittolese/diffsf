# 
# Qui con subprocess replichiamo il processo per usare la API key di Sendgrid
# echo "export SENDGRID_API_KEY='<YOUR_SECRET_KEY>'" > sendgrid.env
# echo "sendgrid.env" >> .gitignore
# 
import subprocess

key = input('Enter your Sengrid API Key ... \n')

with open('sendgrid.env','w') as file:
    exp = f"export SENDGRID_API_KEY='{key}'"
    file.write(exp)

subprocess.call('echo "sendgrid.env" >> .gitignore', shell=True)