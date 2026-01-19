source .env

echo "--- 1. List Available Models ---"
# curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"

echo ""
echo "--- 2. Sanity Check Generation (Gemini 2.5 Flash Lite) ---"
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=$GEMINI_API_KEY" \
-H 'Content-Type: application/json' \
-X POST \
-d '{
  "contents": [{
    "parts":[{"text": "Hello, are you working?"}]
    }]
   }'