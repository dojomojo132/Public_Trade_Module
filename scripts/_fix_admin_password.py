"""Fix admin password hash in DB."""
import bcrypt
import subprocess

hash_bytes = bcrypt.hashpw(b'admin', bcrypt.gensalt(4))
hash_str = hash_bytes.decode()
print(f"Generated hash: {hash_str}")

sql = f"UPDATE users SET password_hash = '{hash_str}' WHERE login = 'admin';"
result = subprocess.run(
    ['docker', 'exec', 'ptm-postgres', 'psql', '-U', 'postgres', '-d', 'ptm', '-c', sql],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr)

# Verify
result2 = subprocess.run(
    ['docker', 'exec', 'ptm-postgres', 'psql', '-U', 'postgres', '-d', 'ptm', '-c',
     "SELECT login, password_hash FROM users WHERE login='admin';"],
    capture_output=True, text=True
)
print(result2.stdout)
