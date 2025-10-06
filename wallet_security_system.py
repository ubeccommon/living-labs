#!/usr/bin/env python3
"""
Wallet Creation Security System
Multi-layer protection against bots and abuse

Security Layers:
1. Rate limiting by IP and email
2. Email verification (optional but recommended)
3. CAPTCHA integration (hCaptcha/reCAPTCHA)
4. Suspicious activity detection
5. Manual approval queue for high-risk requests
6. Daily limits per IP/email
7. Monitoring and alerts

Design Principles Applied:
- Principle #5: Strict async operations
- Principle #9: Integrated rate limiting
- Principle #10: Clear separation of concerns
- Principle #12: Method singularity

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class SecurityCheck:
    """Result of security validation"""
    allowed: bool
    reason: str
    risk_score: int  # 0-100, higher = more risky
    requires_manual_approval: bool = False


class WalletSecurityService:
    """
    Comprehensive security service for wallet creation
    
    Prevents abuse through multiple layers:
    - Rate limiting
    - Email verification
    - CAPTCHA validation
    - Suspicious pattern detection
    - Manual review queue
    """
    
    # Configuration
    MAX_WALLETS_PER_EMAIL = 1  # One wallet per email
    MAX_WALLETS_PER_IP_DAILY = 3  # Max 3 wallets per IP per day
    MAX_WALLETS_PER_IP_HOURLY = 1  # Max 1 per IP per hour
    SUSPICIOUS_THRESHOLD = 70  # Risk score requiring manual review
    
    # Suspicious patterns
    DISPOSABLE_EMAIL_DOMAINS = [
        'tempmail.com', 'guerrillamail.com', 'mailinator.com',
        '10minutemail.com', 'throwaway.email', 'temp-mail.org'
    ]
    
    def __init__(self, database):
        """
        Initialize security service
        
        Args:
            database: Database connection for tracking
        """
        self.database = database
        
        # In-memory rate limiting (Redis recommended for production)
        self._ip_hourly_cache = {}
        self._ip_daily_cache = {}
        self._email_cache = {}
        
        logger.info("Wallet Security Service initialized")
    
    async def validate_wallet_request(
        self,
        email: str,
        name: str,
        ip_address: str,
        captcha_token: Optional[str] = None,
        organization: Optional[str] = None
    ) -> SecurityCheck:
        """
        Comprehensive security validation for wallet creation request
        
        Args:
            email: Steward email address
            name: Steward name
            ip_address: Request IP address
            captcha_token: CAPTCHA token from frontend
            organization: Optional organization name
            
        Returns:
            SecurityCheck with validation result
        """
        risk_score = 0
        reasons = []
        
        try:
            # Layer 1: Email validation
            email_check = await self._validate_email(email)
            risk_score += email_check['risk_score']
            if email_check['issues']:
                reasons.extend(email_check['issues'])
            
            # Layer 2: Rate limiting checks
            rate_check = await self._check_rate_limits(email, ip_address)
            if not rate_check['allowed']:
                return SecurityCheck(
                    allowed=False,
                    reason=rate_check['reason'],
                    risk_score=100
                )
            risk_score += rate_check['risk_score']
            
            # Layer 3: CAPTCHA validation (if enabled)
            if captcha_token:
                captcha_check = await self._validate_captcha(captcha_token, ip_address)
                if not captcha_check['valid']:
                    return SecurityCheck(
                        allowed=False,
                        reason="CAPTCHA validation failed",
                        risk_score=100
                    )
            else:
                # No CAPTCHA increases risk
                risk_score += 20
                reasons.append("No CAPTCHA provided")
            
            # Layer 4: Pattern detection
            pattern_check = await self._detect_suspicious_patterns(
                email, name, ip_address, organization
            )
            risk_score += pattern_check['risk_score']
            if pattern_check['issues']:
                reasons.extend(pattern_check['issues'])
            
            # Layer 5: Database history check
            history_check = await self._check_historical_abuse(email, ip_address)
            risk_score += history_check['risk_score']
            if history_check['issues']:
                reasons.extend(history_check['issues'])
            
            # Determine if manual approval needed
            requires_approval = risk_score >= self.SUSPICIOUS_THRESHOLD
            
            # Decision
            if risk_score >= 90:
                # Too risky - reject
                return SecurityCheck(
                    allowed=False,
                    reason=f"High risk detected: {', '.join(reasons)}",
                    risk_score=risk_score
                )
            elif requires_approval:
                # Suspicious - require manual approval
                logger.warning(f"Wallet request requires approval: {email} (risk: {risk_score})")
                return SecurityCheck(
                    allowed=False,
                    reason="Request requires manual approval",
                    risk_score=risk_score,
                    requires_manual_approval=True
                )
            else:
                # Approved
                logger.info(f"Wallet request approved: {email} (risk: {risk_score})")
                return SecurityCheck(
                    allowed=True,
                    reason="Security checks passed",
                    risk_score=risk_score
                )
                
        except Exception as e:
            logger.error(f"Security validation error: {e}", exc_info=True)
            return SecurityCheck(
                allowed=False,
                reason="Security check failed - try again later",
                risk_score=100
            )
    
    async def _validate_email(self, email: str) -> Dict:
        """
        Validate email address for suspicious patterns
        
        Returns:
            Dict with risk_score and issues list
        """
        risk_score = 0
        issues = []
        
        # Basic format check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            risk_score += 50
            issues.append("Invalid email format")
            return {'risk_score': risk_score, 'issues': issues}
        
        # Check for disposable email domains
        domain = email.split('@')[1].lower()
        if domain in self.DISPOSABLE_EMAIL_DOMAINS:
            risk_score += 60
            issues.append("Disposable email domain detected")
        
        # Check for suspicious patterns
        if '+' in email.split('@')[0]:
            # Gmail plus addressing (can be legitimate, slight risk)
            risk_score += 10
            issues.append("Email alias detected")
        
        # Check for random-looking email
        username = email.split('@')[0]
        if len(username) > 20 and not any(c.isalpha() for c in username[:5]):
            risk_score += 20
            issues.append("Random-looking email username")
        
        return {'risk_score': risk_score, 'issues': issues}
    
    async def _check_rate_limits(self, email: str, ip_address: str) -> Dict:
        """
        Check rate limits for email and IP
        
        Returns:
            Dict with allowed, reason, and risk_score
        """
        now = datetime.utcnow()
        
        # Check email limit (one wallet per email ever)
        email_count = await self._get_wallet_count_by_email(email)
        if email_count >= self.MAX_WALLETS_PER_EMAIL:
            return {
                'allowed': False,
                'reason': f"Email already has {email_count} wallet(s). Limit: {self.MAX_WALLETS_PER_EMAIL}",
                'risk_score': 100
            }
        
        # Check hourly IP limit
        hourly_count = await self._get_wallet_count_by_ip(
            ip_address,
            since=now - timedelta(hours=1)
        )
        if hourly_count >= self.MAX_WALLETS_PER_IP_HOURLY:
            return {
                'allowed': False,
                'reason': f"IP rate limit exceeded. Try again in 1 hour.",
                'risk_score': 100
            }
        
        # Check daily IP limit
        daily_count = await self._get_wallet_count_by_ip(
            ip_address,
            since=now - timedelta(days=1)
        )
        if daily_count >= self.MAX_WALLETS_PER_IP_DAILY:
            return {
                'allowed': False,
                'reason': f"Daily IP limit reached. Try again tomorrow.",
                'risk_score': 100
            }
        
        # Calculate risk based on IP usage
        risk_score = 0
        if daily_count >= 2:
            risk_score += 30
        if hourly_count >= 1:
            risk_score += 20
        
        return {
            'allowed': True,
            'reason': 'Rate limits OK',
            'risk_score': risk_score
        }
    
    async def _validate_captcha(self, token: str, ip_address: str) -> Dict:
        """
        Validate CAPTCHA token with hCaptcha or reCAPTCHA
        
        This is a placeholder - implement with actual CAPTCHA service
        
        Returns:
            Dict with valid boolean
        """
        # TODO: Implement actual CAPTCHA validation
        # For hCaptcha:
        # - POST to https://hcaptcha.com/siteverify
        # - With secret, response (token), remoteip
        
        # For now, just check token exists and is reasonable
        if not token or len(token) < 20:
            return {'valid': False}
        
        logger.info(f"CAPTCHA validation for IP {ip_address}: {token[:10]}...")
        
        # Placeholder: In production, call CAPTCHA API
        return {'valid': True}
    
    async def _detect_suspicious_patterns(
        self,
        email: str,
        name: str,
        ip_address: str,
        organization: Optional[str]
    ) -> Dict:
        """
        Detect suspicious patterns in request data
        
        Returns:
            Dict with risk_score and issues list
        """
        risk_score = 0
        issues = []
        
        # Check for very short/generic names
        if len(name) < 3:
            risk_score += 30
            issues.append("Very short name")
        
        # Check for random-looking names
        if not any(c.isalpha() for c in name):
            risk_score += 40
            issues.append("No letters in name")
        
        # Check for common bot names
        bot_names = ['test', 'bot', 'admin', 'user', 'demo', 'sample']
        if name.lower() in bot_names:
            risk_score += 50
            issues.append("Common bot name detected")
        
        # Check if name and email match reasonably
        name_parts = name.lower().split()
        email_user = email.split('@')[0].lower()
        if name_parts and not any(part in email_user for part in name_parts if len(part) > 2):
            risk_score += 15
            issues.append("Name and email don't match")
        
        return {'risk_score': risk_score, 'issues': issues}
    
    async def _check_historical_abuse(self, email: str, ip_address: str) -> Dict:
        """
        Check database for historical abuse patterns
        
        Returns:
            Dict with risk_score and issues list
        """
        risk_score = 0
        issues = []
        
        try:
            # Check if IP has had failed attempts
            failed_attempts = await self._get_failed_attempts(ip_address)
            if failed_attempts > 5:
                risk_score += 40
                issues.append(f"{failed_attempts} failed attempts from this IP")
            
            # Check if email domain has been used in abuse
            domain = email.split('@')[1]
            domain_wallets = await self._get_wallet_count_by_domain(domain)
            if domain_wallets > 10:
                risk_score += 20
                issues.append(f"Many wallets from this domain: {domain_wallets}")
            
        except Exception as e:
            logger.error(f"Historical check error: {e}")
        
        return {'risk_score': risk_score, 'issues': issues}
    
    async def record_wallet_creation(
        self,
        email: str,
        ip_address: str,
        public_key: str,
        risk_score: int
    ):
        """
        Record successful wallet creation for tracking
        
        Args:
            email: Steward email
            ip_address: Request IP
            public_key: Created wallet public key
            risk_score: Final risk score
        """
        try:
            query = """
                INSERT INTO phenomenological.wallet_security_log
                (email, ip_address, public_key, risk_score, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """
            
            async with self.database.pool.acquire() as conn:
                await conn.execute(
                    query,
                    email,
                    ip_address,
                    public_key,
                    risk_score,
                    datetime.utcnow()
                )
            
            logger.info(f"Recorded wallet creation: {email} from {ip_address}")
            
        except Exception as e:
            logger.error(f"Failed to record wallet creation: {e}")
    
    async def record_failed_attempt(
        self,
        email: str,
        ip_address: str,
        reason: str,
        risk_score: int
    ):
        """
        Record failed wallet creation attempt
        
        Args:
            email: Attempted email
            ip_address: Request IP
            reason: Failure reason
            risk_score: Risk score
        """
        try:
            query = """
                INSERT INTO phenomenological.wallet_failed_attempts
                (email, ip_address, reason, risk_score, attempted_at)
                VALUES ($1, $2, $3, $4, $5)
            """
            
            async with self.database.pool.acquire() as conn:
                await conn.execute(
                    query,
                    email,
                    ip_address,
                    reason,
                    risk_score,
                    datetime.utcnow()
                )
            
            logger.warning(f"Recorded failed attempt: {email} from {ip_address} - {reason}")
            
        except Exception as e:
            logger.error(f"Failed to record attempt: {e}")
    
    # Database helper methods
    
    async def _get_wallet_count_by_email(self, email: str) -> int:
        """Get number of wallets created with this email"""
        try:
            query = """
                SELECT COUNT(*) FROM phenomenological.wallet_creations
                WHERE steward_email = $1
            """
            async with self.database.pool.acquire() as conn:
                result = await conn.fetchval(query, email)
                return result or 0
        except Exception as e:
            logger.error(f"Error checking email count: {e}")
            return 0
    
    async def _get_wallet_count_by_ip(
        self,
        ip_address: str,
        since: datetime
    ) -> int:
        """Get number of wallets created from this IP since timestamp"""
        try:
            query = """
                SELECT COUNT(*) FROM phenomenological.wallet_security_log
                WHERE ip_address = $1 AND created_at >= $2
            """
            async with self.database.pool.acquire() as conn:
                result = await conn.fetchval(query, ip_address, since)
                return result or 0
        except Exception as e:
            logger.error(f"Error checking IP count: {e}")
            return 0
    
    async def _get_failed_attempts(self, ip_address: str) -> int:
        """Get failed attempts from IP in last 24 hours"""
        try:
            query = """
                SELECT COUNT(*) FROM phenomenological.wallet_failed_attempts
                WHERE ip_address = $1 
                AND attempted_at >= $2
            """
            since = datetime.utcnow() - timedelta(days=1)
            async with self.database.pool.acquire() as conn:
                result = await conn.fetchval(query, ip_address, since)
                return result or 0
        except Exception as e:
            logger.error(f"Error checking failed attempts: {e}")
            return 0
    
    async def _get_wallet_count_by_domain(self, domain: str) -> int:
        """Get total wallets created with this email domain"""
        try:
            query = """
                SELECT COUNT(*) FROM phenomenological.wallet_creations
                WHERE steward_email LIKE $1
            """
            pattern = f"%@{domain}"
            async with self.database.pool.acquire() as conn:
                result = await conn.fetchval(query, pattern)
                return result or 0
        except Exception as e:
            logger.error(f"Error checking domain count: {e}")
            return 0
    
    async def close(self):
        """Cleanup resources"""
        pass


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
