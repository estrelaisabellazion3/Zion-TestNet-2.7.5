# ZION 2.7.5 TestNet - Advanced Humanitarian Blockchain

![ZION Logo](https://img.shields.io/badge/ZION-2.7.5%20TestNet-gold)
![License](https://img.shields.io/badge/License-MIT-blue)
![Status](https://img.shields.io/badge/Status-Public%20TestNet-green)

## 🌟 Přehled / Overview

**ZION 2.7.5 TestNet** je pokročilý humanitární blockchain systém s důrazem na bezpečnost, decentralizaci a udržitelnost. Implementuje nejmodernější kryptografické bezpečnostní funkce včetně multi-block reorg ochrany, peer scoring systému a adaptivní obtížnosti.

**ZION 2.7.5 TestNet** is an advanced humanitarian blockchain system focused on security, decentralization, and sustainability. It implements cutting-edge cryptographic security features including multi-block reorg protection, peer scoring systems, and adaptive difficulty.

## 🔒 Klíčové bezpečnostní funkce / Key Security Features

- **Multi-Block Reorg Protection** - Ochrana proti reorganizačním útokům s kumulativní validací práce
- **RPC Authentication & Rate Limiting** - Tokeny pro API přístup s omezením rychlosti požadavků  
- **Peer Scoring & Banning** - Automatické hodnocení a dočasné blokování škodlivých uzlů
- **Median Time Past (MTP)** - Validace timestampů proti manipulaci času
- **LWMA Adaptive Difficulty** - Lineárně vážená adaptivní obtížnost pro stabilní block times
- **Persistent Mempool & Nonce** - Perzistentní transakční pool s ochranou proti replay útokům
- **Comprehensive Metrics** - Prometheus kompatibilní metriky pro monitoring

## 🚀 Rychlý start / Quick Start

### Požadavky / Requirements
```bash
Python 3.9+
SQLite 3
Git
```

### Instalace / Installation
```bash
# Klonování repozitáře
git clone https://github.com/Maitreya-ZionNet/Zion-2.7.5-TestNet.git
cd Zion-2.7.5-TestNet

# Instalace závislostí
pip install -r requirements.txt

# Spuštění uzlu
python start_zion.py
```

### Základní konfigurace / Basic Configuration
```bash
# Nastavení RPC autentifikace
export ZION_RPC_TOKEN="your_secure_token_here"

# Spuštění s vlastním portem
python start_zion.py --rpc-port 8333 --p2p-port 8334
```

## 🏗️ Architektura / Architecture

### Základní komponenty / Core Components
- **`new_zion_blockchain.py`** - Blockchain jádro s journaling a reorg ochranou
- **`zion_p2p_network.py`** - P2P síť s peer scoring systémem  
- **`zion_rpc_server.py`** - HTTP JSON-RPC API s autentifikací
- **`crypto_utils.py`** - ECDSA kryptografické utility
- **`zion_universal_pool_v2.py`** - Mining pool s eco-friendly algoritmy

### Databázové tabulky / Database Tables
```sql
-- Bloky a transakce
blocks, transactions, balances

-- Bezpečnostní persistence  
nonces, mempool, block_journal

-- Peer management
peer_scores, banned_peers
```

## 🔌 API Dokumentace / API Documentation

### RPC Metody / RPC Methods
```bash
# Informace o blockchainu
curl -H "X-ZION-AUTH: your_token" \
  -X POST http://localhost:8332/rpc \
  -d '{"method": "getblockcount"}'

# Mining metriky  
curl http://localhost:8332/metrics

# Odesílání transakce
curl -H "X-ZION-AUTH: your_token" \
  -X POST http://localhost:8332/rpc \
  -d '{"method": "submitrawtransaction", "params": ["signed_tx_hex"]}'
```

### Dostupné metody / Available Methods
- `getblockcount` - Počet bloků v řetězci
- `getdifficulty` - Aktuální obtížnost  
- `getmempoolinfo` - Informace o mempoolu
- `getbalance` - Zůstatek adresy
- `createaddress` - Generování nové adresy
- `submitrawtransaction` - Odeslání podepsané transakce
- `getmetrics` - Systémové metriky

## ⛏️ Mining / Těžba

### Podporované algoritmy / Supported Algorithms
- **RandomX (CPU)** - Baseline (1.0x reward)
- **Yescrypt (CPU)** - Eco bonus (+15% reward)  
- **Autolykos v2 (GPU)** - Eco bonus (+20% reward)

### Spuštění těžby / Start Mining
```bash
# CPU mining (RandomX)
python zion_universal_pool_v2.py --algorithm randomx --threads 4

# Eco-friendly mining (Yescrypt)  
python zion_universal_pool_v2.py --algorithm yescrypt --threads 8
```

## 🧪 Testování / Testing

```bash
# Spuštění všech testů
PYTHONPATH=. python -m pytest tests/

# Jednotlivé test suity
python tests/test_chain_integrity.py      # Integrita řetězce
python tests/test_security_features.py    # Bezpečnostní funkce
python tests/test_persistence_reorg.py    # Persistence a reorgy
```

## 📊 Monitoring & Metriky / Monitoring & Metrics

### Prometheus Endpoint
```bash
curl http://localhost:8332/metrics
```

### Klíčové metriky / Key Metrics
- `zion_block_height` - Aktuální výška blockchainu
- `zion_total_supply` - Celková nabídka tokenů
- `zion_mempool_size` - Počet transakcí v mempoolu  
- `zion_peer_count` - Počet připojených peers
- `zion_banned_peers` - Počet zabanovaných peers
- `zion_auth_failures_total` - Neúspěšné autentifikace
- `zion_rate_limited_total` - Rate limited požadavky

## 🛡️ Bezpečnost / Security

### Doporučená konfigurace / Recommended Configuration
```bash
# Silný RPC token
export ZION_RPC_TOKEN=$(openssl rand -hex 32)

# Rate limiting
export ZION_RATE_LIMIT_PER_MINUTE=60
export ZION_BURST_LIMIT=10

# Peer management
export ZION_MAX_PEERS=50
export ZION_BAN_THRESHOLD=100
```

### Bezpečnostní kontroly / Security Checklist
- ✅ RPC autentifikace aktivována
- ✅ Rate limiting nakonfigurován
- ✅ Firewall pravidla nastavena
- ✅ Monitoring endpoint zabezpečen
- ✅ Peer scoring aktivní

## 🗺️ Roadmap

### Verze 2.7.6 (Q1 2025)
- [ ] Multi-block reorg optimalizace
- [ ] Transakční poplatky (fee market)
- [ ] TLS šifrování P2P komunikace
- [ ] HD wallet podpora

### Verze 2.8.0 (Q2 2025)  
- [ ] Sharding implementace
- [ ] Cross-chain bridge integrace
- [ ] Governance systém
- [ ] Mobile wallet SDK

## 🤝 Přispívání / Contributing

Vítáme příspěvky komunity! Prosím:

1. Forkněte repozitář
2. Vytvořte feature branch (`git checkout -b feature/amazing-feature`)
3. Commitněte změny (`git commit -m 'Add amazing feature'`)  
4. Pushněte branch (`git push origin feature/amazing-feature`)
5. Otevřte Pull Request

### Vývojové pokyny / Development Guidelines
- Všechny změny musí projít testy
- Bezpečnostní funkce vyžadují code review
- Dokumentaci udržujte aktuální (CZ + EN)

## 🐛 Hlášení chyb / Bug Reports

Chyby hlaste prostřednictvím GitHub Issues s následujícími informacemi:
- Verze ZION (`python -c "import zion; print(zion.__version__)"`)
- Operační systém a Python verze  
- Kroky k reprodukci
- Očekávané vs skutečné chování
- Logy (bez citlivých dat)

## 📝 Licence / License

Tento projekt je licencován pod MIT License - viz [LICENSE](LICENSE) soubor.

## 🌐 Komunita / Community

- **Website**: [zion-network.org](https://zion-network.org)
- **Telegram**: [@ZionTestNet](https://t.me/ZionTestNet)
- **Discord**: [ZION Community](https://discord.gg/zion)
- **Twitter**: [@ZionBlockchain](https://twitter.com/ZionBlockchain)

## 🙏 Poděkování / Acknowledgments

Děkujeme všem přispěvatelům, kteří pomohli vytvořit tento humanitární blockchain systém zaměřený na udržitelnost a bezpečnost.

---

**ZION 2.7.5 TestNet** - *Revolutionizing Humanitarian Blockchain Technology* 🌟