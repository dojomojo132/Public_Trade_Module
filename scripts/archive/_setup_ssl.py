"""One-time script to configure Apache HTTPS for PTM mobile cash register."""
import re

HTTPD_CONF = r"C:\Server\Apache24\conf\httpd.conf"

with open(HTTPD_CONF, "r") as f:
    content = f.read()

# 1. Uncomment mod_socache_shmcb
content = content.replace(
    "#LoadModule socache_shmcb_module modules/mod_socache_shmcb.so",
    "LoadModule socache_shmcb_module modules/mod_socache_shmcb.so",
)

# 2. Uncomment mod_ssl
content = content.replace(
    "#LoadModule ssl_module modules/mod_ssl.so",
    "LoadModule ssl_module modules/mod_ssl.so",
)

# 3. Add SSL config at the end (only if not already present)
if "PTM HTTPS Configuration" not in content:
    ssl_block = """
# === PTM HTTPS Configuration ===
Listen 443
SSLSessionCache "shmcb:${SRVROOT}/logs/ssl_scache(512000)"
SSLSessionCacheTimeout 300

<VirtualHost *:443>
    ServerName 192.168.30.35
    DocumentRoot "${SRVROOT}/htdocs"
    SSLEngine on
    SSLCertificateFile "${SRVROOT}/conf/ssl/server.crt"
    SSLCertificateKeyFile "${SRVROOT}/conf/ssl/server.key"
    <Directory "${SRVROOT}/htdocs">
        Require all granted
    </Directory>
</VirtualHost>
"""
    content = content.rstrip() + "\n" + ssl_block
    print("SSL VirtualHost added")
else:
    print("SSL config already present, skipping")

with open(HTTPD_CONF, "w") as f:
    f.write(content)

print("OK: httpd.conf updated")
