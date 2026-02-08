"""Reset Admin Password with Strong Password Requirements"""
import os
import re
from dotenv import load_dotenv
import pymysql
from werkzeug.security import generate_password_hash

load_dotenv()

def validate_password(password):
    """Validate password meets bank-level requirements"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain a number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    if re.search(r'(012|123|234|345|456|567|678|789|abc|bcd|cde)', password, re.IGNORECASE):
        return False, "Password cannot contain sequential characters"
    if re.search(r'(.)\1{2,}', password):
        return False, "Password cannot contain repeated characters"
    
    common = ['password123', 'admin123', '12345678', 'password', 'admin']
    if password.lower() in common:
        return False, "Password is too common"
    
    return True, "Password is strong"

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
user, password, host, port, database = match.groups()

print("=" * 60)
print("RESET ADMIN PASSWORD")
print("=" * 60)
print("\nPassword Requirements:")
print("- Minimum 12 characters")
print("- Must contain: uppercase, lowercase, number, special char")
print("- No sequential characters (123, abc)")
print("- No repeated characters (aaa, 111)")
print("\n")

while True:
    new_password = input("Enter new admin password: ").strip()
    confirm_password = input("Confirm password: ").strip()
    
    if new_password != confirm_password:
        print("[ERROR] Passwords do not match\n")
        continue
    
    is_valid, message = validate_password(new_password)
    if not is_valid:
        print(f"[ERROR] {message}\n")
        continue
    
    break

print("\nUpdating password...")

try:
    conn = pymysql.connect(
        host=host, port=int(port), user=user,
        password=password, database=database,
        charset='utf8mb4', connect_timeout=10
    )
    cursor = conn.cursor()
    
    # Hash password
    password_hash = generate_password_hash(new_password, method='scrypt')
    
    # Update admin password
    cursor.execute("""
        UPDATE users 
        SET password_hash = %s
        WHERE email = 'support@360degreesupply.co.za'
    """, (password_hash,))
    
    conn.commit()
    
    print("\n" + "=" * 60)
    print("SUCCESS - ADMIN PASSWORD UPDATED")
    print("=" * 60)
    print("Email: support@360degreesupply.co.za")
    print("Password: (your new strong password)")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
