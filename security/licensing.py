import hashlib
import platform
import subprocess
import uuid

def get_system_uuid() -> str:
    """
    جلب الرقم التسلسلي للوحة الأم أو الجهاز بحسب نظام التشغيل
    """
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            cmd = "ioreg -l | grep IOPlatformSerialNumber | awk '{print $4}' | tr -d '\"'"
            return subprocess.check_output(cmd, shell=True).decode().strip()
        elif os_name == "Windows":
            cmd = "wmic csproduct get uuid"
            return subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
        elif os_name == "Linux":
            with open("/sys/class/dmi/id/product_uuid") as f:
                return f.read().strip()
    except Exception:
        pass
    
    # خيار بديل (Fallback) في حال تعذر الوصول للـ Hardware ID مباشرة
    return str(uuid.getnode())

def generate_hardware_id() -> str:
    """
    توليد بصمة مشفرة وفريدة للجهاز (HWID Fingerprint)
    """
    raw_id = get_system_uuid()
    return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()

def verify_license(stored_key: str, hardware_id: str) -> bool:
    """
    التحقق من صحة مفتاح الترخيص المدخل
    """
    expected_key = hashlib.sha256(f"PHARMA-{hardware_id}-2026".encode()).hexdigest()[:12].upper()
    return stored_key == expected_key