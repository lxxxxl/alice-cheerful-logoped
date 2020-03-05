#FLASK_APP=api.py flask run --port=5001

HOST=http://127.0.0.1:5001

echo "\nTEST: New user"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 1}}'  $HOST
echo "\nTEST: Invalid response"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"aaa"}}'  $HOST
echo "\nTEST: Valid response"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"Привет"}}'  $HOST
echo "\nTEST: Invalid sentence"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"eee"}}'  $HOST
echo "\nTEST: Valid sentence"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"}}'  $HOST
echo "\nTEST: Help"
curl --header "Content-Type: application/json"  --request POST  --data '{"version":"111","session":{"user_id": "aaa", "new": 0}, "request":{"original_utterance":"помощь"}}'  $HOST
