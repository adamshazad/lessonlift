import google.generativeai as genai

# 🔑 Replace YOUR_API_KEY_HERE with your real Gemini API key
genai.configure(api_key="YOUR_API_KEY_HERE")

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello")
    print("✅ API key works! Response:", response.text)
except Exception as e:
    print("❌ Error:", e)
