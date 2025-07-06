from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
from typing import List, Dict
import string

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Common weak passwords and patterns
COMMON_WEAK_PASSWORDS = {
    'password', 'password123', '123456', 'qwerty', 'abc123', 'letmein',
    'welcome', 'admin', 'user', 'guest', 'test', 'login', 'pass',
    '12345678', '1234567890', 'password1', 'qwerty123', 'welcome123'
}

COMMON_PATTERNS = {
    'sequential': r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',
    'repeated': r'(.)\1{2,}',  # 3+ repeated characters
    'keyboard': r'(qwe|wer|ert|rty|tyu|yui|uio|iop|asd|sdf|dfg|fgh|ghj|hjk|jkl|zxc|xcv|cvb|vbn|bnm)'
}

class PasswordRequest(BaseModel):
    password: str

class PasswordAnalysis(BaseModel):
    strength: str  # 'weak', 'moderate', 'strong'
    score: int  # 0-100
    color: str  # 'red', 'yellow', 'green'
    suggestions: List[str]
    criteria: Dict[str, bool]
    message: str

def analyze_password_strength(password: str) -> PasswordAnalysis:
    """
    Comprehensive password strength analysis
    """
    suggestions = []
    criteria = {
        'length': len(password) >= 12,
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'numbers': bool(re.search(r'[0-9]', password)),
        'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
        'no_common': password.lower() not in COMMON_WEAK_PASSWORDS,
        'no_patterns': not any(re.search(pattern, password.lower()) for pattern in COMMON_PATTERNS.values())
    }
    
    # Calculate base score
    score = 0
    
    # Length scoring (up to 30 points)
    if len(password) >= 12:
        score += 30
    elif len(password) >= 8:
        score += 20
    elif len(password) >= 6:
        score += 10
    else:
        score += 5
    
    # Character variety scoring (up to 40 points)
    if criteria['uppercase']:
        score += 10
    if criteria['lowercase']:
        score += 10
    if criteria['numbers']:
        score += 10
    if criteria['special']:
        score += 10
    
    # Pattern and common password checks (up to 30 points)
    if criteria['no_common']:
        score += 15
    if criteria['no_patterns']:
        score += 15
    
    # Generate suggestions
    if not criteria['length']:
        suggestions.append("Use at least 12 characters for better security")
    if not criteria['uppercase']:
        suggestions.append("Add uppercase letters (A-Z)")
    if not criteria['lowercase']:
        suggestions.append("Add lowercase letters (a-z)")
    if not criteria['numbers']:
        suggestions.append("Include numbers (0-9)")
    if not criteria['special']:
        suggestions.append("Add special characters (!@#$%^&*)")
    if not criteria['no_common']:
        suggestions.append("Avoid common passwords")
    if not criteria['no_patterns']:
        suggestions.append("Avoid predictable patterns (123, abc, qwerty)")
    
    # Additional suggestions based on analysis
    if len(set(password)) < len(password) * 0.7:
        suggestions.append("Use more unique characters")
    
    # Determine strength and color
    if score >= 80:
        strength = "strong"
        color = "green"
        message = "Excellent! Your password is very strong."
    elif score >= 60:
        strength = "moderate"
        color = "yellow"
        message = "Good password, but could be stronger."
    else:
        strength = "weak"
        color = "red"
        message = "Weak password. Please improve it."
    
    # If no suggestions, add encouragement
    if not suggestions:
        suggestions.append("Great job! This is a strong password.")
    
    return PasswordAnalysis(
        strength=strength,
        score=min(score, 100),
        color=color,
        suggestions=suggestions,
        criteria=criteria,
        message=message
    )

@app.get("/")
async def root():
    return {"message": "Password Strength Checker API"}

@app.post("/api/analyze-password")
async def analyze_password(request: PasswordRequest):
    """
    Analyze password strength and return detailed feedback
    """
    try:
        if not request.password:
            return PasswordAnalysis(
                strength="weak",
                score=0,
                color="red",
                suggestions=["Please enter a password"],
                criteria={k: False for k in ['length', 'uppercase', 'lowercase', 'numbers', 'special', 'no_common', 'no_patterns']},
                message="Please enter a password to analyze"
            )
        
        analysis = analyze_password_strength(request.password)
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/password-tips")
async def get_password_tips():
    """
    Get general password security tips
    """
    tips = [
        "Use at least 12 characters for optimal security",
        "Mix uppercase and lowercase letters",
        "Include numbers and special characters",
        "Avoid personal information like names or birthdays",
        "Don't use common words or phrases",
        "Avoid predictable patterns like '123' or 'abc'",
        "Use a unique password for each account",
        "Consider using a password manager",
        "Enable two-factor authentication when available"
    ]
    
    return {"tips": tips}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)