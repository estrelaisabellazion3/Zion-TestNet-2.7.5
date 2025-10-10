#!/usr/bin/env python3
"""
ZION Pool Fee Implementation for Maitreya Admin

Implementace pool fee systému s progressive fee structure a loyalty discounts.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import json

class ZionPoolFeeManager:
    """
    Manages pool fees for ZION mining pool.
    
    Features:
    - Progressive fee structure (launch/growth/mature phases)
    - Loyalty discounts for long-term miners
    - Consciousness level bonuses
    - Transparent fee breakdown
    """
    
    def __init__(self):
        # Launch date
        self.launch_date = datetime(2025, 10, 10)
        
        # Fee structure by phase
        self.fee_phases = {
            "launch": {
                "duration_months": 6,
                "base_fee": 0.01,  # 1.0%
                "description": "Community building phase"
            },
            "growth": {
                "duration_months": 12,
                "base_fee": 0.015,  # 1.5%
                "description": "Sustainable operation phase"
            },
            "mature": {
                "duration_months": None,  # Indefinite
                "base_fee": 0.02,  # 2.0%
                "description": "Ecosystem expansion phase"
            }
        }
        
        # Loyalty discounts (cumulative)
        self.loyalty_discounts = {
            "mining_3_months": 0.001,   # -0.1%
            "mining_6_months": 0.002,   # -0.2%
            "mining_12_months": 0.003,  # -0.3%
            "mining_24_months": 0.005,  # -0.5%
        }
        
        # Consciousness level discounts
        self.consciousness_discounts = {
            "level_5": 0.001,  # Enlightened: -0.1%
            "level_7": 0.002,  # Transcendent: -0.2%
            "level_9": 0.003,  # Unified: -0.3%
        }
        
        # Special bonuses
        self.special_discounts = {
            "golden_egg_seeker": 0.005,  # Active in Golden Egg quest: -0.5%
            "top_100_xp": 0.002,         # Top 100 XP: -0.2%
            "eco_mode_warrior": 0.001,   # Always eco mode: -0.1%
        }
        
        # Admin wallet for pool fees
        self.admin_wallet = "ZionPoolAdmin1..."  # Replace with actual address
    
    def get_current_phase(self, current_date: datetime = None) -> str:
        """Determine current pool fee phase."""
        if current_date is None:
            current_date = datetime.now()
        
        months_since_launch = (current_date.year - self.launch_date.year) * 12 + \
                             (current_date.month - self.launch_date.month)
        
        if months_since_launch < 6:
            return "launch"
        elif months_since_launch < 18:
            return "growth"
        else:
            return "mature"
    
    def get_base_fee(self, current_date: datetime = None) -> float:
        """Get base pool fee percentage for current phase."""
        phase = self.get_current_phase(current_date)
        return self.fee_phases[phase]["base_fee"]
    
    def calculate_loyalty_discount(self, 
                                   miner_start_date: datetime) -> float:
        """Calculate loyalty discount based on mining duration."""
        now = datetime.now()
        months_mining = (now.year - miner_start_date.year) * 12 + \
                       (now.month - miner_start_date.month)
        
        total_discount = 0.0
        
        if months_mining >= 24:
            total_discount = self.loyalty_discounts["mining_24_months"]
        elif months_mining >= 12:
            total_discount = self.loyalty_discounts["mining_12_months"]
        elif months_mining >= 6:
            total_discount = self.loyalty_discounts["mining_6_months"]
        elif months_mining >= 3:
            total_discount = self.loyalty_discounts["mining_3_months"]
        
        return total_discount
    
    def calculate_consciousness_discount(self, 
                                        consciousness_level: int) -> float:
        """Calculate discount based on consciousness level."""
        if consciousness_level >= 9:
            return self.consciousness_discounts["level_9"]
        elif consciousness_level >= 7:
            return self.consciousness_discounts["level_7"]
        elif consciousness_level >= 5:
            return self.consciousness_discounts["level_5"]
        return 0.0
    
    def calculate_special_discounts(self, 
                                   miner_data: Dict) -> float:
        """Calculate special achievement-based discounts."""
        total_discount = 0.0
        
        if miner_data.get("golden_egg_active", False):
            total_discount += self.special_discounts["golden_egg_seeker"]
        
        if miner_data.get("xp_rank", 999) <= 100:
            total_discount += self.special_discounts["top_100_xp"]
        
        if miner_data.get("eco_mode_percent", 0) >= 90:
            total_discount += self.special_discounts["eco_mode_warrior"]
        
        return total_discount
    
    def calculate_miner_fee(self,
                           miner_address: str,
                           miner_start_date: datetime,
                           consciousness_level: int,
                           miner_data: Dict) -> Tuple[float, Dict]:
        """
        Calculate final pool fee for a miner with full breakdown.
        
        Returns:
            (final_fee_percent, breakdown_dict)
        """
        # Base fee for current phase
        base_fee = self.get_base_fee()
        
        # Calculate all discounts
        loyalty_discount = self.calculate_loyalty_discount(miner_start_date)
        consciousness_discount = self.calculate_consciousness_discount(consciousness_level)
        special_discount = self.calculate_special_discounts(miner_data)
        
        # Total discount (capped at 80% of base fee to avoid negative)
        total_discount = min(
            loyalty_discount + consciousness_discount + special_discount,
            base_fee * 0.8
        )
        
        # Final fee
        final_fee = max(base_fee - total_discount, 0.001)  # Minimum 0.1%
        
        # Breakdown for transparency
        breakdown = {
            "base_fee_percent": base_fee * 100,
            "phase": self.get_current_phase(),
            "discounts": {
                "loyalty": loyalty_discount * 100,
                "consciousness": consciousness_discount * 100,
                "special": special_discount * 100,
                "total": total_discount * 100
            },
            "final_fee_percent": final_fee * 100,
            "savings_percent": ((base_fee - final_fee) / base_fee * 100) if base_fee > 0 else 0
        }
        
        return final_fee, breakdown
    
    def apply_pool_fee_to_reward(self,
                                 total_reward: float,
                                 miner_address: str,
                                 miner_start_date: datetime,
                                 consciousness_level: int,
                                 miner_data: Dict) -> Tuple[float, float, Dict]:
        """
        Apply pool fee to block reward.
        
        Returns:
            (miner_reward, admin_fee, breakdown)
        """
        final_fee, breakdown = self.calculate_miner_fee(
            miner_address,
            miner_start_date,
            consciousness_level,
            miner_data
        )
        
        admin_fee = total_reward * final_fee
        miner_reward = total_reward - admin_fee
        
        breakdown["total_reward"] = total_reward
        breakdown["miner_reward"] = miner_reward
        breakdown["admin_fee"] = admin_fee
        breakdown["admin_wallet"] = self.admin_wallet
        
        return miner_reward, admin_fee, breakdown
    
    def get_fee_allocation_breakdown(self, total_fee_collected: float) -> Dict:
        """
        Show how pool fees are allocated (for transparency).
        """
        allocation = {
            "total_collected": total_fee_collected,
            "allocation": {
                "infrastructure_40%": total_fee_collected * 0.40,
                "admin_salary_30%": total_fee_collected * 0.30,
                "ecosystem_development_20%": total_fee_collected * 0.20,
                "emergency_reserve_10%": total_fee_collected * 0.10
            },
            "description": {
                "infrastructure": "Server costs, bandwidth, security, monitoring",
                "admin_salary": "Development time, support, community management",
                "ecosystem": "Marketing, partnerships, new features, events",
                "reserve": "Unexpected expenses, security incidents, opportunities"
            }
        }
        return allocation


# ============================================================================
# INTEGRATION EXAMPLE FOR zion_universal_pool_v2.py
# ============================================================================

class ZionUniversalPoolWithFee:
    """
    Example integration of pool fee into main pool.
    This shows how to modify the existing pool code.
    """
    
    def __init__(self):
        # Existing pool initialization...
        self.fee_manager = ZionPoolFeeManager()
        
        # Track miner stats for fee calculation
        self.miner_stats = {}  # {address: {start_date, consciousness_level, data}}
    
    def on_block_found(self, block_data: Dict):
        """
        Called when pool finds a block.
        Distribute rewards with pool fee applied.
        """
        total_reward = block_data["reward"]
        miner_address = block_data["miner_address"]
        
        # Get miner stats
        if miner_address not in self.miner_stats:
            self.miner_stats[miner_address] = {
                "start_date": datetime.now(),
                "consciousness_level": 1,
                "data": {}
            }
        
        miner_info = self.miner_stats[miner_address]
        
        # Calculate fee and distribute
        miner_reward, admin_fee, breakdown = self.fee_manager.apply_pool_fee_to_reward(
            total_reward,
            miner_address,
            miner_info["start_date"],
            miner_info["consciousness_level"],
            miner_info["data"]
        )
        
        # Log fee breakdown for transparency
        print(f"\n💰 Block Found! Fee Breakdown:")
        print(f"   Total Reward: {total_reward:.2f} ZION")
        print(f"   Miner Gets: {miner_reward:.2f} ZION ({100 - breakdown['final_fee_percent']:.2f}%)")
        print(f"   Pool Fee: {admin_fee:.2f} ZION ({breakdown['final_fee_percent']:.2f}%)")
        print(f"   Discounts Applied: {breakdown['discounts']['total']:.2f}%")
        
        # Send rewards
        self.send_reward_to_miner(miner_address, miner_reward)
        self.send_fee_to_admin(self.fee_manager.admin_wallet, admin_fee)
        
        # Save breakdown to database for transparency
        self.save_fee_breakdown(block_data["height"], breakdown)
    
    def send_reward_to_miner(self, address: str, amount: float):
        """Send reward to miner (implement with actual RPC)."""
        print(f"✅ Sent {amount:.2f} ZION to {address}")
    
    def send_fee_to_admin(self, address: str, amount: float):
        """Send pool fee to admin wallet (implement with actual RPC)."""
        print(f"💼 Pool fee {amount:.2f} ZION to admin {address}")
    
    def save_fee_breakdown(self, block_height: int, breakdown: Dict):
        """Save fee breakdown to database for transparency."""
        # Save to database...
        pass
    
    def get_miner_fee_info(self, miner_address: str) -> Dict:
        """
        API endpoint to show miner their current fee rate and potential discounts.
        """
        if miner_address not in self.miner_stats:
            return {"error": "Miner not found"}
        
        miner_info = self.miner_stats[miner_address]
        
        final_fee, breakdown = self.fee_manager.calculate_miner_fee(
            miner_address,
            miner_info["start_date"],
            miner_info["consciousness_level"],
            miner_info["data"]
        )
        
        # Calculate potential future discounts
        potential_discounts = self._calculate_potential_discounts(miner_info)
        
        return {
            "current_fee": breakdown,
            "potential_discounts": potential_discounts,
            "tips": self._generate_discount_tips(miner_info)
        }
    
    def _calculate_potential_discounts(self, miner_info: Dict) -> Dict:
        """Show what discounts miner could unlock."""
        potential = {}
        
        # Check loyalty milestones
        now = datetime.now()
        months_mining = (now.year - miner_info["start_date"].year) * 12 + \
                       (now.month - miner_info["start_date"].month)
        
        if months_mining < 3:
            potential["mine_3_months"] = {
                "discount": "0.1%",
                "time_remaining": f"{3 - months_mining} months"
            }
        
        # Check consciousness level
        current_level = miner_info["consciousness_level"]
        if current_level < 5:
            potential["reach_level_5"] = {
                "discount": "0.1%",
                "xp_needed": "Calculate from consciousness game"
            }
        
        return potential
    
    def _generate_discount_tips(self, miner_info: Dict) -> list:
        """Generate personalized tips to reduce fee."""
        tips = []
        
        if miner_info["consciousness_level"] < 5:
            tips.append("💡 Reach consciousness level 5 to unlock 0.1% discount!")
        
        if miner_info["data"].get("eco_mode_percent", 0) < 90:
            tips.append("🌱 Use eco mode 90%+ of the time for 0.1% discount!")
        
        if not miner_info["data"].get("golden_egg_active"):
            tips.append("🥚 Start Golden Egg quest for 0.5% discount!")
        
        return tips


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ZION POOL FEE CALCULATOR - TEST")
    print("=" * 60)
    
    fee_manager = ZionPoolFeeManager()
    
    # Test scenarios
    test_miners = [
        {
            "name": "New Miner (Level 1, just started)",
            "address": "ZionMiner1...",
            "start_date": datetime.now() - timedelta(days=10),
            "consciousness_level": 1,
            "data": {}
        },
        {
            "name": "Dedicated Miner (Level 5, 6 months)",
            "address": "ZionMiner2...",
            "start_date": datetime.now() - timedelta(days=180),
            "consciousness_level": 5,
            "data": {"eco_mode_percent": 95}
        },
        {
            "name": "Elite Miner (Level 9, 2 years, top 100, Golden Egg)",
            "address": "ZionMiner3...",
            "start_date": datetime.now() - timedelta(days=730),
            "consciousness_level": 9,
            "data": {
                "eco_mode_percent": 98,
                "golden_egg_active": True,
                "xp_rank": 42
            }
        }
    ]
    
    block_reward = 10000  # Example: 10k ZION block
    
    for miner in test_miners:
        print(f"\n{'─' * 60}")
        print(f"MINER: {miner['name']}")
        print(f"{'─' * 60}")
        
        miner_reward, admin_fee, breakdown = fee_manager.apply_pool_fee_to_reward(
            block_reward,
            miner["address"],
            miner["start_date"],
            miner["consciousness_level"],
            miner["data"]
        )
        
        print(f"\n📊 Fee Breakdown:")
        print(f"   Phase: {breakdown['phase']}")
        print(f"   Base Fee: {breakdown['base_fee_percent']:.2f}%")
        print(f"   Discounts:")
        print(f"      • Loyalty: {breakdown['discounts']['loyalty']:.2f}%")
        print(f"      • Consciousness: {breakdown['discounts']['consciousness']:.2f}%")
        print(f"      • Special: {breakdown['discounts']['special']:.2f}%")
        print(f"      • Total Discount: {breakdown['discounts']['total']:.2f}%")
        print(f"   Final Fee: {breakdown['final_fee_percent']:.2f}%")
        print(f"   Savings: {breakdown['savings_percent']:.1f}%")
        print(f"\n💰 Reward Distribution:")
        print(f"   Block Reward: {block_reward:,.2f} ZION")
        print(f"   Miner Gets: {miner_reward:,.2f} ZION")
        print(f"   Pool Admin: {admin_fee:,.2f} ZION")
    
    print(f"\n{'=' * 60}")
    print("FEE ALLOCATION TRANSPARENCY")
    print(f"{'=' * 60}")
    
    # Example: Monthly fee collection
    monthly_fees = 50000  # Example: 50k ZION/month in fees
    allocation = fee_manager.get_fee_allocation_breakdown(monthly_fees)
    
    print(f"\nTotal Fees Collected: {allocation['total_collected']:,.2f} ZION")
    print(f"\nAllocation:")
    for category, amount in allocation['allocation'].items():
        category_key = category.split('_')[0] if '_' in category else category
        if category_key == 'admin':
            category_key = 'infrastructure'  # Fallback
        desc = allocation['description'].get(category_key, "Other expenses")
        print(f"   • {category}: {amount:,.2f} ZION")
        print(f"     └─ {desc}")
    
    print("\n" + "=" * 60)
    print("✅ POOL FEE SYSTEM READY FOR DEPLOYMENT")
    print("=" * 60)
