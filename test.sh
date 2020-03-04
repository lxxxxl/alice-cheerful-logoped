#FLASK_APP=api.py flask run --port=5001

echo "\nTEST: New user"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 1}}'  http://127.0.0.1:5001
echo "\nTEST: Invalid response"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"aaa"}}'  http://127.0.0.1:5001
echo "\nTEST: Valid response"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"Привет"}}'  http://127.0.0.1:5001
echo "\nTEST: Invalid sentence"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"eee"}}'  http://127.0.0.1:5001
echo "\nTEST: Valid sentence"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"}}'  http://127.0.0.1:5001
