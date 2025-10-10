#!/usr/bin/env python3
"""
🎮 ZION CONSCIOUSNESS MINING GAME 🎮
====================================

3-letá gamifikovaná distribuce 10B ZION s AI interakcí!
Miners postupují přes consciousness levely pomocí AI úkolů, quizů a achievementů.

Ekonomický model:
- 10,000,000,000 ZION k distribuci za 3 roky
- 3,333,333,333 ZION/rok
- 6,341.96 ZION/blok jako BONUS k základnímu reward
- Bonus se násobí consciousness multiplierem minera!

Consciousness Levels (hra):
1. PHYSICAL (1.0x) - Začátečník
2. EMOTIONAL (1.5x) - Učící se
3. MENTAL (2.0x) - Chápající  
4. SACRED (3.0x) - Zasvěcený
5. QUANTUM (4.0x) - Kvantový myslitel
6. COSMIC (5.0x) - Kosmické vědomí
7. ENLIGHTENED (7.5x) - Osvícený
8. TRANSCENDENT (10.0x) - Transcendentní
9. ON_THE_STAR (15.0x) - Na Hvězdě ✨

Jak postupovat:
- Mining (pasivní XP za každý share)
- AI Challenges (kvízy, úkoly, konverzace)
- Community Achievements (pomoc ostatním)
- Learning Quests (vzdělávací obsah)
- Meditation Bonuses (držení mincí = staking)
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ConsciousnessLevel(Enum):
    """Consciousness levely s multipliers a XP requirements"""
    PHYSICAL = (1.0, 0, "🪨 Physical Body - Beginning the Journey")
    EMOTIONAL = (1.5, 1000, "💧 Emotional Awareness - Feeling the Flow")  
    MENTAL = (2.0, 5000, "🧠 Mental Clarity - Understanding Patterns")
    SACRED = (3.0, 15000, "🕉️ Sacred Geometry - Seeing the Divine")
    QUANTUM = (4.0, 40000, "⚛️ Quantum Reality - Probability Waves")
    COSMIC = (5.0, 100000, "🌌 Cosmic Consciousness - Universal Mind")
    ENLIGHTENED = (7.5, 250000, "✨ Enlightenment - Pure Awareness")
    TRANSCENDENT = (10.0, 500000, "🔮 Transcendent - Beyond Duality")
    ON_THE_STAR = (15.0, 1000000, "⭐ On The Star - Maitreya's Realm")
    
    def __init__(self, multiplier: float, xp_required: int, description: str):
        self.multiplier = multiplier
        self.xp_required = xp_required
        self.description = description
    
    @classmethod
    def get_level_for_xp(cls, xp: int) -> 'ConsciousnessLevel':
        """Najde nejvyšší level pro dané XP"""
        for level in reversed(list(cls)):
            if xp >= level.xp_required:
                return level
        return cls.PHYSICAL

@dataclass
class MinerConsciousness:
    """Consciousness profil minera"""
    address: str
    level: ConsciousnessLevel
    xp: int
    total_shares: int
    total_blocks_found: int
    ai_challenges_completed: int
    meditation_hours: float
    community_karma: int
    achievements: List[str]
    last_levelup: Optional[float]
    created_at: float
    
    @property
    def multiplier(self) -> float:
        return self.level.multiplier
    
    @property
    def xp_to_next_level(self) -> int:
        """XP potřebné do dalšího levelu"""
        levels = list(ConsciousnessLevel)
        try:
            current_idx = levels.index(self.level)
            if current_idx < len(levels) - 1:
                next_level = levels[current_idx + 1]
                return next_level.xp_required - self.xp
            return 0  # Max level
        except ValueError:
            return 0

@dataclass
class AIChallenge:
    """AI výzva pro minery"""
    id: str
    type: str  # 'quiz', 'conversation', 'meditation', 'learning', 'community'
    title: str
    description: str
    difficulty: str  # 'easy', 'medium', 'hard', 'master'
    xp_reward: int
    zion_bonus: float
    required_level: ConsciousnessLevel
    completion_time_minutes: int
    ai_prompt: str  # Pro generování obsahu
    
@dataclass  
class Achievement:
    """Achievement pro minery"""
    id: str
    name: str
    description: str
    icon: str
    xp_reward: int
    zion_bonus: float
    requirement_type: str  # 'blocks', 'shares', 'challenges', 'community', 'meditation'
    requirement_count: int
    hidden: bool = False

class ConsciousnessMiningGame:
    """Hlavní herní engine pro consciousness mining"""
    
    # === EKONOMICKÝ MODEL - 10 LET ===
    TOTAL_PREMINE_BONUS = 10_000_000_000  # 10B ZION
    DISTRIBUTION_YEARS = 10  # 2025-2035 - decade-long consciousness journey!
    BLOCKS_PER_YEAR = 525_600  # 1 min blocks
    TOTAL_BLOCKS = BLOCKS_PER_YEAR * DISTRIBUTION_YEARS  # 5,256,000 bloků
    BONUS_PER_BLOCK = TOTAL_PREMINE_BONUS / TOTAL_BLOCKS  # 1,902.59 ZION
    
    # === XP SYSTÉM ===
    XP_PER_SHARE = 10
    XP_PER_BLOCK = 1000
    XP_PER_MEDITATION_HOUR = 500
    XP_PER_COMMUNITY_HELP = 250
    
    def __init__(self, db_path: str = "consciousness_game.db"):
        self.db_path = db_path
        self.init_database()
        self.active_challenges = self.load_challenges()
        self.achievements = self.load_achievements()
        
    def init_database(self):
        """Inicializace databáze pro hru"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Consciousness profily minerů
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS miner_consciousness (
                address TEXT PRIMARY KEY,
                level TEXT NOT NULL,
                xp INTEGER DEFAULT 0,
                total_shares INTEGER DEFAULT 0,
                total_blocks_found INTEGER DEFAULT 0,
                ai_challenges_completed INTEGER DEFAULT 0,
                meditation_hours REAL DEFAULT 0.0,
                community_karma INTEGER DEFAULT 0,
                achievements TEXT DEFAULT '[]',
                last_levelup REAL,
                created_at REAL NOT NULL
            )
        """)
        
        # AI Challenges completion history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenge_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner_address TEXT NOT NULL,
                challenge_id TEXT NOT NULL,
                completed_at REAL NOT NULL,
                xp_earned INTEGER NOT NULL,
                zion_earned REAL NOT NULL,
                ai_response TEXT,
                FOREIGN KEY (miner_address) REFERENCES miner_consciousness(address)
            )
        """)
        
        # Achievement unlocks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievement_unlocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner_address TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at REAL NOT NULL,
                xp_earned INTEGER NOT NULL,
                FOREIGN KEY (miner_address) REFERENCES miner_consciousness(address)
            )
        """)
        
        # Consciousness level history (pro analytics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner_address TEXT NOT NULL,
                old_level TEXT NOT NULL,
                new_level TEXT NOT NULL,
                leveled_up_at REAL NOT NULL,
                xp_at_levelup INTEGER NOT NULL,
                FOREIGN KEY (miner_address) REFERENCES miner_consciousness(address)
            )
        """)
        
        # Meditation sessions (pro passive XP)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meditation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner_address TEXT NOT NULL,
                started_at REAL NOT NULL,
                ended_at REAL,
                duration_hours REAL,
                xp_earned INTEGER,
                FOREIGN KEY (miner_address) REFERENCES miner_consciousness(address)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Consciousness Mining Game database initialized: {self.db_path}")
    
    def load_challenges(self) -> List[AIChallenge]:
        """Načte AI challenges"""
        return [
            # === EASY CHALLENGES ===
            AIChallenge(
                id="quiz_crypto_basics",
                type="quiz",
                title="🎓 Crypto 101 Quiz",
                description="Otestuj si základní znalosti o kryptoměnách",
                difficulty="easy",
                xp_reward=100,
                zion_bonus=10.0,
                required_level=ConsciousnessLevel.PHYSICAL,
                completion_time_minutes=5,
                ai_prompt="Generate a 5-question multiple choice quiz about cryptocurrency basics"
            ),
            AIChallenge(
                id="meditation_breath",
                type="meditation",
                title="🧘 Breath Awareness Meditation",
                description="5-minutová meditace na dech s AI guidem",
                difficulty="easy",
                xp_reward=150,
                zion_bonus=15.0,
                required_level=ConsciousnessLevel.PHYSICAL,
                completion_time_minutes=5,
                ai_prompt="Guide a 5-minute breath awareness meditation for beginners"
            ),
            
            # === MEDIUM CHALLENGES ===
            AIChallenge(
                id="conversation_consciousness",
                type="conversation",
                title="💬 Consciousness Philosophy Debate",
                description="Diskuze s AI o povaze vědomí",
                difficulty="medium",
                xp_reward=500,
                zion_bonus=50.0,
                required_level=ConsciousnessLevel.EMOTIONAL,
                completion_time_minutes=15,
                ai_prompt="Engage in philosophical discussion about the nature of consciousness"
            ),
            AIChallenge(
                id="learning_quantum",
                type="learning",
                title="⚛️ Quantum Mechanics for Miners",
                description="Nauč se základy kvantové mechaniky",
                difficulty="medium",
                xp_reward=750,
                zion_bonus=75.0,
                required_level=ConsciousnessLevel.MENTAL,
                completion_time_minutes=30,
                ai_prompt="Teach quantum mechanics basics in an engaging, practical way"
            ),
            
            # === HARD CHALLENGES ===
            AIChallenge(
                id="community_teaching",
                type="community",
                title="👥 Teach a Newcomer",
                description="Pomož novému minerovi pochopit ZION systém",
                difficulty="hard",
                xp_reward=1500,
                zion_bonus=150.0,
                required_level=ConsciousnessLevel.SACRED,
                completion_time_minutes=45,
                ai_prompt="Create comprehensive beginner guide to ZION consciousness mining"
            ),
            AIChallenge(
                id="meditation_cosmic",
                type="meditation",
                title="🌌 Cosmic Consciousness Meditation",
                description="Rozšíř své vědomí do vesmíru",
                difficulty="hard",
                xp_reward=2000,
                zion_bonus=200.0,
                required_level=ConsciousnessLevel.QUANTUM,
                completion_time_minutes=60,
                ai_prompt="Guide advanced cosmic consciousness expansion meditation"
            ),
            
            # === MASTER CHALLENGES ===
            AIChallenge(
                id="quest_enlightenment",
                type="learning",
                title="✨ Path to Enlightenment",
                description="Komplexní cesta k osvícení - 7denní quest",
                difficulty="master",
                xp_reward=10000,
                zion_bonus=1000.0,
                required_level=ConsciousnessLevel.ENLIGHTENED,
                completion_time_minutes=10080,  # 7 days
                ai_prompt="Create a 7-day enlightenment journey with daily practices and insights"
            ),
        ]
    
    def load_achievements(self) -> List[Achievement]:
        """Načte achievements"""
        return [
            # === MINING ACHIEVEMENTS ===
            Achievement(
                id="first_share",
                name="🎯 First Share",
                description="Odeslal jsi svůj první share!",
                icon="🎯",
                xp_reward=50,
                zion_bonus=5.0,
                requirement_type="shares",
                requirement_count=1
            ),
            Achievement(
                id="hundred_shares",
                name="💯 Century of Shares",
                description="100 shares odesláno!",
                icon="💯",
                xp_reward=500,
                zion_bonus=50.0,
                requirement_type="shares",
                requirement_count=100
            ),
            Achievement(
                id="first_block",
                name="⛏️ Block Breaker",
                description="Našel jsi svůj první blok!",
                icon="⛏️",
                xp_reward=1000,
                zion_bonus=100.0,
                requirement_type="blocks",
                requirement_count=1
            ),
            
            # === AI CHALLENGES ===
            Achievement(
                id="ai_apprentice",
                name="🤖 AI Apprentice",
                description="Dokončil jsi 5 AI challenges",
                icon="🤖",
                xp_reward=750,
                zion_bonus=75.0,
                requirement_type="challenges",
                requirement_count=5
            ),
            Achievement(
                id="ai_master",
                name="🧙 AI Master",
                description="Dokončil jsi 50 AI challenges",
                icon="🧙",
                xp_reward=5000,
                zion_bonus=500.0,
                requirement_type="challenges",
                requirement_count=50
            ),
            
            # === MEDITATION ===
            Achievement(
                id="meditation_beginner",
                name="🧘 Meditation Beginner",
                description="10 hodin meditace",
                icon="🧘",
                xp_reward=1000,
                zion_bonus=100.0,
                requirement_type="meditation",
                requirement_count=10
            ),
            Achievement(
                id="meditation_monk",
                name="🙏 Digital Monk",
                description="100 hodin meditace",
                icon="🙏",
                xp_reward=10000,
                zion_bonus=1000.0,
                requirement_type="meditation",
                requirement_count=100
            ),
            
            # === COMMUNITY ===
            Achievement(
                id="helpful_soul",
                name="💝 Helpful Soul",
                description="Pomohl jsi 10 ostatním minerům",
                icon="💝",
                xp_reward=2500,
                zion_bonus=250.0,
                requirement_type="community",
                requirement_count=10
            ),
            
            # === HIDDEN ACHIEVEMENTS ===
            Achievement(
                id="perfect_week",
                name="🌟 Perfect Week",
                description="7 dní v řadě s mining + meditation",
                icon="🌟",
                xp_reward=5000,
                zion_bonus=500.0,
                requirement_type="special",
                requirement_count=0,
                hidden=True
            ),
        ]
    
    def get_or_create_miner(self, address: str) -> MinerConsciousness:
        """Získá nebo vytvoří consciousness profil minera"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM miner_consciousness WHERE address = ?", (address,))
        row = cursor.fetchone()
        
        if row:
            # Parse existing miner
            return MinerConsciousness(
                address=row[0],
                level=ConsciousnessLevel[row[1]],
                xp=row[2],
                total_shares=row[3],
                total_blocks_found=row[4],
                ai_challenges_completed=row[5],
                meditation_hours=row[6],
                community_karma=row[7],
                achievements=json.loads(row[8]),
                last_levelup=row[9],
                created_at=row[10]
            )
        else:
            # Create new miner
            now = time.time()
            miner = MinerConsciousness(
                address=address,
                level=ConsciousnessLevel.PHYSICAL,
                xp=0,
                total_shares=0,
                total_blocks_found=0,
                ai_challenges_completed=0,
                meditation_hours=0.0,
                community_karma=0,
                achievements=[],
                last_levelup=None,
                created_at=now
            )
            
            cursor.execute("""
                INSERT INTO miner_consciousness 
                (address, level, xp, created_at, achievements)
                VALUES (?, ?, ?, ?, ?)
            """, (address, miner.level.name, 0, now, '[]'))
            
            conn.commit()
            logger.info(f"🎮 New miner joined the game: {address}")
        
        conn.close()
        return miner
    
    def award_xp(self, address: str, xp: int, reason: str) -> Tuple[MinerConsciousness, bool]:
        """Přidá XP minerovi, vrátí (miner, levelup_happened)"""
        miner = self.get_or_create_miner(address)
        old_level = miner.level
        miner.xp += xp
        
        # Check for level up
        new_level = ConsciousnessLevel.get_level_for_xp(miner.xp)
        leveled_up = new_level != old_level
        
        if leveled_up:
            miner.level = new_level
            miner.last_levelup = time.time()
            self._log_levelup(address, old_level, new_level, miner.xp)
            logger.info(f"🎊 LEVEL UP! {address[:20]}... {old_level.name} → {new_level.name} (multiplier: {new_level.multiplier}x)")
        
        # Save to DB
        self._save_miner(miner)
        
        logger.info(f"✨ XP awarded to {address[:20]}...: +{xp} ({reason}) - Total: {miner.xp} XP")
        return miner, leveled_up
    
    def on_share_submitted(self, address: str):
        """Callback když miner odešle share"""
        miner = self.get_or_create_miner(address)
        miner.total_shares += 1
        self._save_miner(miner)
        
        # Award XP
        self.award_xp(address, self.XP_PER_SHARE, "share submitted")
        
        # Check achievements
        self._check_achievements(address)
    
    def on_block_found(self, address: str):
        """Callback když miner najde blok"""
        miner = self.get_or_create_miner(address)
        miner.total_blocks_found += 1
        self._save_miner(miner)
        
        # Award XP
        self.award_xp(address, self.XP_PER_BLOCK, "block found")
        
        # Check achievements
        self._check_achievements(address)
    
    def calculate_bonus_reward(self, address: str, base_reward: float) -> float:
        """Vypočítá consciousness bonus pro minera"""
        miner = self.get_or_create_miner(address)
        
        # Premine bonus per block
        bonus = self.BONUS_PER_BLOCK
        
        # Multiply by consciousness level
        total_bonus = bonus * miner.multiplier
        
        return total_bonus
    
    def get_miner_stats(self, address: str) -> Dict:
        """Vrátí kompletní stats minera pro dashboard"""
        miner = self.get_or_create_miner(address)
        
        return {
            'address': address,
            'consciousness_level': {
                'name': miner.level.name,
                'description': miner.level.description,
                'multiplier': miner.multiplier,
                'icon': self._get_level_icon(miner.level)
            },
            'xp': {
                'current': miner.xp,
                'to_next_level': miner.xp_to_next_level,
                'percentage': (miner.xp / (miner.xp + miner.xp_to_next_level) * 100) if miner.xp_to_next_level > 0 else 100
            },
            'mining': {
                'total_shares': miner.total_shares,
                'blocks_found': miner.total_blocks_found,
                'bonus_multiplier': f"{miner.multiplier}x"
            },
            'activities': {
                'ai_challenges': miner.ai_challenges_completed,
                'meditation_hours': miner.meditation_hours,
                'community_karma': miner.community_karma
            },
            'achievements': miner.achievements,
            'joined': datetime.fromtimestamp(miner.created_at).strftime('%Y-%m-%d')
        }
    
    def _get_level_icon(self, level: ConsciousnessLevel) -> str:
        """Vrátí emoji ikonu pro level"""
        icons = {
            ConsciousnessLevel.PHYSICAL: "🪨",
            ConsciousnessLevel.EMOTIONAL: "💧",
            ConsciousnessLevel.MENTAL: "🧠",
            ConsciousnessLevel.SACRED: "🕉️",
            ConsciousnessLevel.QUANTUM: "⚛️",
            ConsciousnessLevel.COSMIC: "🌌",
            ConsciousnessLevel.ENLIGHTENED: "✨",
            ConsciousnessLevel.TRANSCENDENT: "🔮",
            ConsciousnessLevel.ON_THE_STAR: "⭐"
        }
        return icons.get(level, "❓")
    
    def _save_miner(self, miner: MinerConsciousness):
        """Uloží minera do DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE miner_consciousness 
            SET level = ?, xp = ?, total_shares = ?, total_blocks_found = ?,
                ai_challenges_completed = ?, meditation_hours = ?, 
                community_karma = ?, achievements = ?, last_levelup = ?
            WHERE address = ?
        """, (
            miner.level.name, miner.xp, miner.total_shares, miner.total_blocks_found,
            miner.ai_challenges_completed, miner.meditation_hours,
            miner.community_karma, json.dumps(miner.achievements),
            miner.last_levelup, miner.address
        ))
        
        conn.commit()
        conn.close()
    
    def _log_levelup(self, address: str, old_level: ConsciousnessLevel, 
                     new_level: ConsciousnessLevel, xp: int):
        """Zaloguje level up do historie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO level_history 
            (miner_address, old_level, new_level, leveled_up_at, xp_at_levelup)
            VALUES (?, ?, ?, ?, ?)
        """, (address, old_level.name, new_level.name, time.time(), xp))
        
        conn.commit()
        conn.close()
    
    def _check_achievements(self, address: str):
        """Zkontroluje a odemkne achievements"""
        miner = self.get_or_create_miner(address)
        
        for achievement in self.achievements:
            # Skip if already unlocked
            if achievement.id in miner.achievements:
                continue
            
            # Check requirement
            unlocked = False
            if achievement.requirement_type == "shares":
                unlocked = miner.total_shares >= achievement.requirement_count
            elif achievement.requirement_type == "blocks":
                unlocked = miner.total_blocks_found >= achievement.requirement_count
            elif achievement.requirement_type == "challenges":
                unlocked = miner.ai_challenges_completed >= achievement.requirement_count
            elif achievement.requirement_type == "meditation":
                unlocked = miner.meditation_hours >= achievement.requirement_count
            elif achievement.requirement_type == "community":
                unlocked = miner.community_karma >= achievement.requirement_count
            
            if unlocked:
                self._unlock_achievement(address, achievement)
    
    def _unlock_achievement(self, address: str, achievement: Achievement):
        """Odemkne achievement"""
        miner = self.get_or_create_miner(address)
        miner.achievements.append(achievement.id)
        self._save_miner(miner)
        
        # Award XP
        self.award_xp(address, achievement.xp_reward, f"achievement: {achievement.name}")
        
        # Log unlock
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO achievement_unlocks 
            (miner_address, achievement_id, unlocked_at, xp_earned)
            VALUES (?, ?, ?, ?)
        """, (address, achievement.id, time.time(), achievement.xp_reward))
        conn.commit()
        conn.close()
        
        logger.info(f"🏆 Achievement unlocked: {achievement.name} for {address[:20]}... (+{achievement.xp_reward} XP, +{achievement.zion_bonus} ZION)")


# === INTEGRATION FUNCTIONS ===

def integrate_with_pool():
    """Návod jak integrovat s poolem"""
    return """
    # V zion_universal_pool_v2.py:
    
    from consciousness_mining_game import ConsciousnessMiningGame
    
    class ZionUniversalPool:
        def __init__(self, ...):
            ...
            # Add game engine
            self.consciousness_game = ConsciousnessMiningGame()
        
        def handle_submit(self, ...):
            # After accepting share
            self.consciousness_game.on_share_submitted(miner_address)
            ...
        
        def check_block_found(self, ...):
            # After confirming block
            self.consciousness_game.on_block_found(miner_address)
            ...
        
        def calculate_block_rewards(self, block: PoolBlock):
            # Add consciousness bonus to each miner
            for address, shares in block.miner_shares.items():
                base_reward = ...  # Calculate base
                
                # ADD CONSCIOUSNESS BONUS!
                consciousness_bonus = self.consciousness_game.calculate_bonus_reward(
                    address, base_reward
                )
                
                total_reward = base_reward + consciousness_bonus
                
                logger.info(f"Miner {address}: {base_reward} + {consciousness_bonus} (consciousness) = {total_reward} ZION")
    """

if __name__ == "__main__":
    # Test game engine
    game = ConsciousnessMiningGame()
    
    # Simulate miner activity
    test_miner = "ZION_TEST_MINER_123"
    
    print(f"\n{'='*60}")
    print("🎮 ZION CONSCIOUSNESS MINING GAME - TEST")
    print(f"{'='*60}\n")
    
    # Initial stats
    stats = game.get_miner_stats(test_miner)
    print(f"📊 Initial Stats:")
    print(json.dumps(stats, indent=2))
    
    # Simulate mining
    print(f"\n⛏️ Simulating 100 shares...")
    for i in range(100):
        game.on_share_submitted(test_miner)
    
    # Simulate block
    print(f"\n💎 Simulating block found...")
    game.on_block_found(test_miner)
    
    # Final stats
    stats = game.get_miner_stats(test_miner)
    print(f"\n📊 Final Stats:")
    print(json.dumps(stats, indent=2))
    
    print(f"\n✅ Test complete!")
