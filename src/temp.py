import os
import subprocess

print(f"Current API Key :  {os.environ["OPENAI_API_KEY"]}")
OPENAI_API_KEY = input("Enter you API Key : ")       
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  
subprocess.run(['setx', 'OPENAI_API_KEY', OPENAI_API_KEY], check=True) 

print(f"Current API Key :  {os.environ["OPENAI_API_KEY"]}")