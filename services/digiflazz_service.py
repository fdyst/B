import requests
import random
import string

# Dummy Digiflazz integration
DIGIFLAZZ_API_KEY = "YOUR_API_KEY"
DIGIFLAZZ_URL = "https://api.digiflazz.com/v1/transaction"

def send_order_to_vendor(product_code: str, phone_number: str, price: float):
    """
    Simulasi kirim order ke Digiflazz
    """
    # Biasanya pake requests.post ke API Digiflazz asli
    # Contoh response dummy:
    vendor_order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    serial_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    status = "success"  # bisa success, pending, failed

    return {
        "vendor_order_id": vendor_order_id,
        "serial_number": serial_number,
        "status": status
    }