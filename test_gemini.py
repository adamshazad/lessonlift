import google.generativeai as genai

genai.configure(api_key="AIzaSyA_R4e7mPPVJLGEDHuKJgTzPCDjZsvOpsk")

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Write a short funny poem about teachers.")
    print(response.text)
except Exception as e:
    print("Error:", e)
