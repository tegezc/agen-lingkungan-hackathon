import firebase_admin
from firebase_admin import credentials, messaging

if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK berhasil diinisialisasi untuk notifikasi.")

def send_multicast_notification(tokens: list, title: str, body: str):
    """
    Mengirim notifikasi ke banyak perangkat dengan cara iterasi (satu per satu).
    Lebih andal daripada send_multicast jika API legacy bermasalah.
    """
    if not tokens:
        print("Tidak ada token, tidak ada notifikasi yang dikirim.")
        return None

    success_count = 0
    failure_count = 0
    failed_tokens = []

    # Iterasi melalui setiap token dan kirim notifikasi secara individual
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        try:
            messaging.send(message)
            success_count += 1
        except Exception as e:
            print(f"Gagal mengirim notifikasi ke token {token}: {e}")
            failure_count += 1
            failed_tokens.append(token)

    print(f"Notifikasi berhasil dikirim ke {success_count} dari {len(tokens)} perangkat.")
    if failure_count > 0:
        print(f"Token yang gagal: {failed_tokens}")

    # Kita buat objek respons tiruan agar formatnya mirip
    class MockResponse:
        def __init__(self, success, failure):
            self.success_count = success
            self.failure_count = failure

    return MockResponse(success_count, failure_count)
    