# ZION Miner - Ubuntu Package

## Description
High-performance cryptocurrency miner for ZION TestNet 2.7.5. This is the official production-ready mining client that connects to ZION mining pools using real Stratum protocol - no simulations.

## Features
- **Real Mining**: Direct Stratum protocol connection to mining pools
- **High Performance**: Optimized for 500K+ H/s on standard hardware  
- **Multi-Algorithm**: RandomX and YesCrypt algorithm support
- **Production Ready**: Robust error handling and automatic reconnection
- **Systemd Integration**: Full Linux service management
- **Secure**: Runs as dedicated system user with restricted permissions
- **Configurable**: JSON-based configuration with runtime parameters

## Quick Start

### 1. Installation
```bash
sudo dpkg -i zion-miner_1.0.0_amd64.deb
sudo apt-get install -f  # Fix any missing dependencies
```

### 2. Configuration  
Edit the configuration file:
```bash
sudo nano /etc/zion-miner/config.json
```

Update the wallet address and pool settings:
```json
{
  "pool_host": "your-pool-host.com", 
  "pool_port": 3335,
  "wallet_address": "your-zion-wallet-address",
  "worker_name": "your-worker-name"
}
```

### 3. Start Mining
```bash
# Start the service
sudo systemctl start zion-miner

# Enable auto-start on boot
sudo systemctl enable zion-miner

# Check status
sudo systemctl status zion-miner

# View logs
sudo journalctl -u zion-miner -f
```

## Manual Usage
You can also run the miner manually:
```bash
# Run with default config
zion-miner

# Run with custom config  
zion-miner --config /path/to/config.json

# Run with command line options
zion-miner --pool pool.example.com:3335 --wallet YourWalletAddress
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `pool_host` | localhost | Mining pool hostname |
| `pool_port` | 3335 | Mining pool port |
| `wallet_address` | Zion1DefaultWallet | Your ZION wallet address |  
| `worker_name` | ZION-Ubuntu-Production | Worker identifier |
| `log_level` | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `connection_retries` | 5 | Connection retry attempts |
| `retry_delay` | 10 | Seconds between retries |
| `report_interval` | 30 | Status report frequency (seconds) |

## Service Management

```bash
# Service status
sudo systemctl status zion-miner

# Start mining
sudo systemctl start zion-miner

# Stop mining  
sudo systemctl stop zion-miner

# Restart service
sudo systemctl restart zion-miner

# Enable auto-start
sudo systemctl enable zion-miner

# Disable auto-start
sudo systemctl disable zion-miner

# View logs
sudo journalctl -u zion-miner -f

# View recent logs
sudo journalctl -u zion-miner --since "1 hour ago"
```

## File Locations

- **Executable**: `/usr/bin/zion-miner`
- **Configuration**: `/etc/zion-miner/config.json`
- **Service File**: `/lib/systemd/system/zion-miner.service`
- **Data Directory**: `/var/lib/zion-miner/`
- **Log Files**: `/var/lib/zion-miner/logs/miner.log`
- **Documentation**: `/usr/share/doc/zion-miner/`

## Troubleshooting

### Connection Issues
```bash
# Check network connectivity
ping your-pool-host.com

# Verify pool port is open
telnet your-pool-host.com 3335

# Check service status
sudo systemctl status zion-miner

# View detailed logs
sudo journalctl -u zion-miner --no-pager
```

### Performance Issues
- Monitor CPU usage: `htop`
- Check system resources: `free -h`
- Verify no thermal throttling: `sensors`
- Review log for errors: `sudo journalctl -u zion-miner -p err`

### Permission Issues
```bash
# Fix permissions
sudo chown -R zion-miner:zion-miner /var/lib/zion-miner
sudo chmod 644 /etc/zion-miner/config.json
sudo chmod +x /usr/bin/zion-miner
```

## Uninstallation
```bash
# Stop and disable service
sudo systemctl stop zion-miner
sudo systemctl disable zion-miner

# Remove package
sudo dpkg -r zion-miner

# Remove configuration and data (optional)
sudo rm -rf /etc/zion-miner
sudo rm -rf /var/lib/zion-miner
```

## Support
- **GitHub**: https://github.com/estrelaisabellazion3/Zion-TestNet-2.7.5
- **Issues**: https://github.com/estrelaisabellazion3/Zion-TestNet-2.7.5/issues
- **Documentation**: https://github.com/estrelaisabellazion3/Zion-TestNet-2.7.5/wiki

## License
MIT License - See LICENSE file for details

## Version
ZION Miner v1.0.0 (Ubuntu Release)
Built: $(date)
Architecture: amd64