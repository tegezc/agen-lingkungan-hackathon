import firebase_admin
from firebase_admin import credentials, messaging

if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully for notifications.")

def send_multicast_notification(tokens: list, title: str, body: str):
    """
    Sends notifications to multiple devices by iterating (one by one).
    More reliable than send_multicast if the legacy API has issues.
    """
    if not tokens:
        print("No tokens provided, no notification sent.")
        return None

    success_count = 0
    failure_count = 0
    failed_tokens = []

    # Iterate through each token and send a notification individually
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        try:
            messaging.send(message)
            success_count += 1
        except Exception as e:
            print(f"Failed to send notification to token {token}: {e}")
            failure_count += 1
            failed_tokens.append(token)

    print(f"Successfully sent notifications to {success_count} of {len(tokens)} devices.")
    if failure_count > 0:
        print(f"Failed tokens: {failed_tokens}")

    # Create a mock response object so the format is similar
    class MockResponse:
        def __init__(self, success, failure):
            self.success_count = success
            self.failure_count = failure

    return MockResponse(success_count, failure_count)
    