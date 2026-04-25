# core/config.py
# Configurações doaa sistema

# IP da máquina na rede local (para QR Code e acesso externo)
# Descubra seu IP com o comando: ipconfig (Windows) ou ifconfig (Linux/Mac)
# Exemplo: '192.168.1.100'
REDE_IP = '192.168.18.8'  # ← SUBSTITUA PELO SEU IP REAL

# Porta do servidor
PORTA = 8000

# URL completa do site
SITE_URL = f'http://{REDE_IP}:{PORTA}'