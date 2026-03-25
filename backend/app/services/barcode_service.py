"""Service de décodage de code-barres et QR codes via pyzbar."""

from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol

from app.core import BarcodeDecodeError


def decode_barcode(image: Image.Image) -> tuple[str, str]:
    """Tente de décoder un code EAN/UPC ou QR Code depuis une image PIL.

    Args:
        image: Image PIL à analyser

    Returns:
        Tuple (code_décodé, type_symbole) — type_symbole est 'EAN' ou 'QRCODE'

    Raises:
        BarcodeDecodeError: Si aucun code-barres/QR n'est détecté
    """
    results = decode(
        image,
        symbols=[
            ZBarSymbol.EAN13,
            ZBarSymbol.EAN8,
            ZBarSymbol.UPCA,
            ZBarSymbol.QRCODE,
        ],
    )

    if not results:
        raise BarcodeDecodeError("Aucun code-barres ou QR code détecté dans l'image")

    result = results[0]
    code = result.data.decode("utf-8")
    symbol_type = result.type  # e.g. 'EAN13', 'QRCODE'

    if symbol_type == "QRCODE":
        return code, "QRCODE"

    return code, "EAN"
