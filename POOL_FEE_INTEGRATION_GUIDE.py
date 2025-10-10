"""
NÁVOD: Jak integrovat Pool Fee do zion_universal_pool_v2.py

Tento soubor obsahuje konkrétní kroky pro přidání pool fee systému.
"""

# ============================================================================
# KROK 1: Import na začátku souboru
# ============================================================================

# Přidej tento import na začátek zion_universal_pool_v2.py (asi řádek 20-30)
from pool_fee_implementation import ZionPoolFeeManager

# ============================================================================
# KROK 2: Inicializace v __init__
# ============================================================================

# V __init__ metodě ZionUniversalPool třídy, přidej (asi řádek 100-150):

class ZionUniversalPool:
    def __init__(self, config):
        # ... existing code ...
        
        # Pool fee manager
        self.fee_manager = ZionPoolFeeManager()
        
        # Admin wallet pro pool fees (ZMĚŇ NA SVOU ADRESU!)
        self.pool_admin_wallet = "ZionPoolAdminXXXXXXXXXXXXXXXXXXXXX"
        
        # Track miner start dates for loyalty discounts
        self.miner_first_seen = {}  # {address: datetime}
        
        # ... rest of existing code ...

# ============================================================================
# KROK 3: Track kdy miner začal minovat
# ============================================================================

# V metodě kde přijímáš první share od minera (asi v handle_share nebo podobně):

def on_miner_first_share(self, miner_address):
    """Called when miner submits first share ever"""
    if miner_address not in self.miner_first_seen:
        from datetime import datetime
        self.miner_first_seen[miner_address] = datetime.now()
        
        # Save to database
        self.db.execute(
            "INSERT INTO miner_start_dates (address, first_seen) VALUES (?, ?)",
            (miner_address, datetime.now())
        )

# ============================================================================
# KROK 4: Aplikuj pool fee při block found
# ============================================================================

# V metodě kde distribuuješ block reward (asi on_block_found nebo distribute_reward):

def distribute_block_reward(self, block_height, total_reward, shares):
    """
    Distribute block reward to miners with pool fee applied.
    
    Args:
        block_height: Height of found block
        total_reward: Total ZION reward for this block
        shares: Dict of {miner_address: share_count}
    """
    
    from datetime import datetime
    
    # Calculate total shares
    total_shares = sum(shares.values())
    
    # For each miner
    for miner_address, miner_shares in shares.items():
        
        # Calculate miner's portion based on shares
        miner_portion = (miner_shares / total_shares)
        miner_base_reward = total_reward * miner_portion
        
        # Get miner info for fee calculation
        miner_start_date = self.miner_first_seen.get(
            miner_address, 
            datetime.now()  # Default to now if not tracked yet
        )
        
        # Get consciousness level from game
        consciousness_level = self.consciousness_game.get_miner_level(miner_address)
        
        # Get miner data for special discounts
        miner_data = {
            "golden_egg_active": self.consciousness_game.is_golden_egg_active(miner_address),
            "xp_rank": self.consciousness_game.get_miner_rank(miner_address),
            "eco_mode_percent": self.get_miner_eco_usage_percent(miner_address)
        }
        
        # Apply pool fee with all discounts
        final_reward, admin_fee, fee_breakdown = self.fee_manager.apply_pool_fee_to_reward(
            miner_base_reward,
            miner_address,
            miner_start_date,
            consciousness_level,
            miner_data
        )
        
        # Log fee breakdown (for transparency and debugging)
        self.logger.info(f"Block {block_height} - Miner {miner_address[:8]}...")
        self.logger.info(f"  Base reward: {miner_base_reward:.2f} ZION")
        self.logger.info(f"  Fee: {fee_breakdown['final_fee_percent']:.2f}% ({admin_fee:.2f} ZION)")
        self.logger.info(f"  Discounts: {fee_breakdown['discounts']['total']:.2f}%")
        self.logger.info(f"  Final reward: {final_reward:.2f} ZION")
        
        # Send reward to miner
        self.send_payment(miner_address, final_reward)
        
        # Accumulate admin fees (send in batch later to save tx fees)
        if not hasattr(self, 'pending_admin_fees'):
            self.pending_admin_fees = 0
        self.pending_admin_fees += admin_fee
        
        # Save to database for transparency
        self.save_payment_record(
            block_height=block_height,
            miner_address=miner_address,
            base_reward=miner_base_reward,
            pool_fee=admin_fee,
            final_reward=final_reward,
            fee_breakdown=fee_breakdown
        )
    
    # Send accumulated admin fees (if threshold reached)
    if self.pending_admin_fees >= 100:  # Send when we have 100+ ZION
        self.send_payment(self.pool_admin_wallet, self.pending_admin_fees)
        self.logger.info(f"💰 Pool admin fee payment: {self.pending_admin_fees:.2f} ZION")
        self.pending_admin_fees = 0

# ============================================================================
# KROK 5: API endpoint pro fee info
# ============================================================================

# Přidej Flask/FastAPI endpoint (podle toho co používáš):

@app.route('/api/pool/fee_info/<address>')
def get_miner_fee_info(address):
    """
    Get miner's current fee rate and potential discounts.
    
    Returns JSON with:
    - current_fee: Current fee percentage
    - base_fee: Base fee for current phase
    - discounts: Breakdown of all discounts
    - savings: % saved vs base fee
    - tips: How to reduce fee further
    """
    
    from datetime import datetime
    
    # Get miner info
    miner_start_date = pool.miner_first_seen.get(address, datetime.now())
    consciousness_level = pool.consciousness_game.get_miner_level(address)
    
    miner_data = {
        "golden_egg_active": pool.consciousness_game.is_golden_egg_active(address),
        "xp_rank": pool.consciousness_game.get_miner_rank(address),
        "eco_mode_percent": pool.get_miner_eco_usage_percent(address)
    }
    
    # Calculate fee
    final_fee, breakdown = pool.fee_manager.calculate_miner_fee(
        address,
        miner_start_date,
        consciousness_level,
        miner_data
    )
    
    # Generate tips for improvement
    tips = []
    
    # Loyalty tips
    from datetime import datetime
    months_mining = (datetime.now() - miner_start_date).days // 30
    if months_mining < 3:
        tips.append(f"⏰ Mine for {3 - months_mining} more months to unlock 0.1% loyalty discount!")
    elif months_mining < 6:
        tips.append(f"⏰ Mine for {6 - months_mining} more months to unlock 0.2% loyalty discount!")
    elif months_mining < 12:
        tips.append(f"⏰ Mine for {12 - months_mining} more months to unlock 0.3% loyalty discount!")
    
    # Consciousness tips
    if consciousness_level < 5:
        tips.append("🧘 Reach consciousness level 5 for 0.1% discount!")
    elif consciousness_level < 7:
        tips.append("🧘 Reach consciousness level 7 for 0.2% discount!")
    elif consciousness_level < 9:
        tips.append("🧘 Reach consciousness level 9 for 0.3% discount!")
    
    # Special achievement tips
    if not miner_data.get("golden_egg_active"):
        tips.append("🥚 Start the Golden Egg quest for 0.5% discount!")
    
    if miner_data.get("xp_rank", 999) > 100:
        tips.append("🏆 Get into top 100 XP for 0.2% discount!")
    
    if miner_data.get("eco_mode_percent", 0) < 90:
        tips.append("🌱 Use eco mode 90%+ of the time for 0.1% discount!")
    
    return {
        "address": address,
        "current_fee": breakdown,
        "tips": tips,
        "next_discount_milestone": _get_next_milestone(miner_start_date, consciousness_level, miner_data)
    }

def _get_next_milestone(start_date, level, data):
    """Calculate next achievable discount milestone"""
    from datetime import datetime
    
    months = (datetime.now() - start_date).days // 30
    
    # Check loyalty milestones
    if months < 3:
        return {"type": "loyalty", "name": "3 months mining", "discount": "0.1%", "eta": "X days"}
    elif level < 5:
        return {"type": "consciousness", "name": "Level 5", "discount": "0.1%", "eta": "Y XP needed"}
    # ... etc
    
    return None

# ============================================================================
# KROK 6: Dashboard widget pro fee display
# ============================================================================

# HTML/JavaScript pro dashboard (přidej do template):

"""
<div class="fee-info-widget">
    <h3>💰 Your Pool Fee Rate</h3>
    <div class="fee-current">
        <span class="fee-number" id="current-fee">1.0%</span>
        <span class="fee-label">Current Fee</span>
    </div>
    
    <div class="fee-breakdown">
        <div class="fee-row">
            <span>Base Fee:</span>
            <span id="base-fee">1.0%</span>
        </div>
        <div class="fee-row discount">
            <span>Loyalty Discount:</span>
            <span id="loyalty-discount">-0.2%</span>
        </div>
        <div class="fee-row discount">
            <span>Consciousness Discount:</span>
            <span id="consciousness-discount">-0.1%</span>
        </div>
        <div class="fee-row discount">
            <span>Special Discounts:</span>
            <span id="special-discount">-0.1%</span>
        </div>
    </div>
    
    <div class="fee-savings">
        You're saving <span id="savings-percent">40%</span> on pool fees! 🎉
    </div>
    
    <div class="fee-tips">
        <h4>💡 How to reduce your fee further:</h4>
        <ul id="fee-tips-list">
            <!-- Populated by JavaScript -->
        </ul>
    </div>
</div>

<script>
// Fetch fee info from API
async function updateFeeInfo() {
    const address = getCurrentMinerAddress(); // Your function to get address
    const response = await fetch(`/api/pool/fee_info/${address}`);
    const data = await response.json();
    
    // Update display
    document.getElementById('current-fee').textContent = 
        data.current_fee.final_fee_percent.toFixed(2) + '%';
    document.getElementById('base-fee').textContent = 
        data.current_fee.base_fee_percent.toFixed(2) + '%';
    document.getElementById('loyalty-discount').textContent = 
        '-' + data.current_fee.discounts.loyalty.toFixed(2) + '%';
    document.getElementById('consciousness-discount').textContent = 
        '-' + data.current_fee.discounts.consciousness.toFixed(2) + '%';
    document.getElementById('special-discount').textContent = 
        '-' + data.current_fee.discounts.special.toFixed(2) + '%';
    document.getElementById('savings-percent').textContent = 
        data.current_fee.savings_percent.toFixed(0) + '%';
    
    // Update tips
    const tipsList = document.getElementById('fee-tips-list');
    tipsList.innerHTML = '';
    data.tips.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        tipsList.appendChild(li);
    });
}

// Update every 60 seconds
setInterval(updateFeeInfo, 60000);
updateFeeInfo(); // Initial load
</script>
"""

# ============================================================================
# KROK 7: Transparency page
# ============================================================================

# Create /pool/transparency page showing where fees go:

@app.route('/pool/transparency')
def pool_transparency():
    """Show where pool fees are allocated"""
    
    # Get last 30 days of fee collection
    total_fees_collected = db.execute(
        "SELECT SUM(pool_fee) FROM payments WHERE timestamp > datetime('now', '-30 days')"
    ).fetchone()[0] or 0
    
    # Get allocation breakdown
    allocation = pool.fee_manager.get_fee_allocation_breakdown(total_fees_collected)
    
    return render_template('transparency.html', 
                          allocation=allocation,
                          total_fees=total_fees_collected)

# ============================================================================
# KROK 8: Database schema
# ============================================================================

# Add these tables to your database:

"""
CREATE TABLE IF NOT EXISTS miner_start_dates (
    address TEXT PRIMARY KEY,
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_height INTEGER NOT NULL,
    miner_address TEXT NOT NULL,
    base_reward REAL NOT NULL,
    pool_fee REAL NOT NULL,
    final_reward REAL NOT NULL,
    fee_breakdown TEXT,  -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_fee_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    txid TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_miner ON payments(miner_address);
CREATE INDEX idx_payments_block ON payments(block_height);
CREATE INDEX idx_payments_timestamp ON payments(timestamp);
"""

# ============================================================================
# KROK 9: Testing
# ============================================================================

# Test fee calculation:

def test_pool_fee():
    from datetime import datetime, timedelta
    from pool_fee_implementation import ZionPoolFeeManager
    
    fee_manager = ZionPoolFeeManager()
    
    # Test case 1: New miner
    print("\n=== TEST 1: New Miner ===")
    reward, fee, breakdown = fee_manager.apply_pool_fee_to_reward(
        total_reward=10000,
        miner_address="ZionTest1...",
        miner_start_date=datetime.now(),
        consciousness_level=1,
        miner_data={}
    )
    print(f"10k block -> Miner gets {reward:.2f}, Pool gets {fee:.2f} ({breakdown['final_fee_percent']:.2f}%)")
    
    # Test case 2: Veteran miner
    print("\n=== TEST 2: Veteran Miner ===")
    reward, fee, breakdown = fee_manager.apply_pool_fee_to_reward(
        total_reward=10000,
        miner_address="ZionTest2...",
        miner_start_date=datetime.now() - timedelta(days=730),  # 2 years
        consciousness_level=9,
        miner_data={
            "golden_egg_active": True,
            "xp_rank": 42,
            "eco_mode_percent": 98
        }
    )
    print(f"10k block -> Miner gets {reward:.2f}, Pool gets {fee:.2f} ({breakdown['final_fee_percent']:.2f}%)")
    print(f"Total discounts: {breakdown['discounts']['total']:.2f}%")

if __name__ == "__main__":
    test_pool_fee()

# ============================================================================
# KROK 10: Deployment checklist
# ============================================================================

"""
PŘED NASAZENÍM:

1. ✅ Změň pool_admin_wallet na svou skutečnou adresu
2. ✅ Otestuj pool_fee_implementation.py samostatně
3. ✅ Přidej database tables (miner_start_dates, payments)
4. ✅ Integruj do block distribution logic
5. ✅ Přidaj API endpoint /api/pool/fee_info/<address>
6. ✅ Vytvoř dashboard widget pro fee display
7. ✅ Vytvoř transparency page
8. ✅ Test na testnet s fake blocks
9. ✅ Announcej minery o 1% launch fee (marketing!)
10. ✅ Připrav FAQ o pool fee a discounts

OZNÁMENÍ PRO MINERY:

"🎉 ZION Pool launches with only 1% fee!

But that's just the beginning...

✨ Mine for 6 months? Get 0.2% discount!
🧘 Reach consciousness level 5? Another 0.1% off!
🥚 Hunt for the Golden Egg? -0.5% fee!
🏆 Top 100 XP? -0.2% fee!

Elite miners pay as low as 0.2% - that's 80% off!

Fair fees. Real rewards. Consciousness evolution.

Welcome to the future of mining. 🚀"
"""

print(__doc__)
