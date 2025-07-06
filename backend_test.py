import requests
import unittest
import json
import re

class PasswordStrengthAPITester:
    def __init__(self, base_url="https://5c54b8c0-8140-458b-8d5f-aa08a1a631d8.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json() if response.text else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_password_tips(self):
        """Test the password tips endpoint"""
        return self.run_test(
            "Password Tips Endpoint",
            "GET",
            "api/password-tips",
            200
        )

    def test_analyze_empty_password(self):
        """Test analyzing an empty password"""
        return self.run_test(
            "Analyze Empty Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": ""}
        )

    def test_analyze_weak_password(self):
        """Test analyzing a weak password"""
        return self.run_test(
            "Analyze Weak Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": "123"}
        )

    def test_analyze_moderate_password(self):
        """Test analyzing a moderate password"""
        return self.run_test(
            "Analyze Moderate Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": "Password123"}
        )

    def test_analyze_strong_password(self):
        """Test analyzing a strong password"""
        return self.run_test(
            "Analyze Strong Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": "MySecure#Password2024!"}
        )

    def test_analyze_common_password(self):
        """Test analyzing a common password"""
        return self.run_test(
            "Analyze Common Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": "password123"}
        )

    def test_analyze_pattern_password(self):
        """Test analyzing a password with patterns"""
        return self.run_test(
            "Analyze Pattern Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": "abcdef123456"}
        )

    def test_analyze_unicode_password(self):
        """Test analyzing a password with unicode characters"""
        return self.run_test(
            "Analyze Unicode Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": "Пароль123!"}
        )

    def test_analyze_very_long_password(self):
        """Test analyzing a very long password"""
        return self.run_test(
            "Analyze Very Long Password",
            "POST",
            "api/analyze-password",
            200,
            data={"password": "ThisIsAVeryLongPasswordThatShouldStillBeAnalyzedCorrectly!2024@"}
        )
        
    def test_generate_passwords(self):
        """Test the password generation endpoint"""
        success, data = self.run_test(
            "Generate Passwords",
            "GET",
            "api/generate-passwords",
            200
        )
        
        if success:
            suggestions = data.get('suggestions', [])
            count = data.get('count', 0)
            
            # Check if we got the expected number of suggestions (default is 3)
            if count == 3 and len(suggestions) == 3:
                print(f"  - Successfully generated {count} password suggestions")
                
                # Verify all passwords are strong
                all_strong = True
                for suggestion in suggestions:
                    # Check if password exists and has a score
                    if 'password' not in suggestion or 'score' not in suggestion:
                        all_strong = False
                        print(f"  - ❌ Invalid suggestion format: {suggestion}")
                        continue
                        
                    password = suggestion['password']
                    score = suggestion['score']
                    
                    # Verify password meets criteria for strong passwords
                    has_uppercase = bool(re.search(r'[A-Z]', password))
                    has_lowercase = bool(re.search(r'[a-z]', password))
                    has_numbers = bool(re.search(r'[0-9]', password))
                    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
                    has_length = len(password) >= 12
                    
                    if not (has_uppercase and has_lowercase and has_numbers and has_special and has_length and score >= 80):
                        all_strong = False
                        print(f"  - ❌ Generated password doesn't meet strong criteria: {password}")
                        
                if all_strong:
                    print("  - ✅ All generated passwords meet strong criteria")
                    self.tests_passed += 1
                else:
                    print("  - ❌ Some generated passwords don't meet strong criteria")
                    self.tests_run += 1
            else:
                print(f"  - ❌ Expected 3 suggestions, got {count}")
                self.tests_run += 1
                
        return success, data
        
    def test_generate_passwords_custom_count(self):
        """Test the password generation endpoint with custom count"""
        success, data = self.run_test(
            "Generate Passwords (Custom Count)",
            "GET",
            "api/generate-passwords?count=5",
            200
        )
        
        if success:
            suggestions = data.get('suggestions', [])
            count = data.get('count', 0)
            
            if count == 5 and len(suggestions) == 5:
                print(f"  - Successfully generated {count} password suggestions")
                self.tests_passed += 1
            else:
                print(f"  - ❌ Expected 5 suggestions, got {count}")
                self.tests_run += 1
                
        return success, data

    def run_all_tests(self):
        """Run all tests and print results"""
        print("🚀 Starting Password Strength API Tests...")
        
        # Test root endpoint
        self.test_root_endpoint()
        
        # Test password tips endpoint
        success, tips_data = self.test_password_tips()
        if success:
            print(f"  - Retrieved {len(tips_data.get('tips', []))} password tips")
        
        # Test password analysis with various passwords
        self.test_analyze_empty_password()
        
        success, weak_data = self.test_analyze_weak_password()
        if success:
            print(f"  - Weak password score: {weak_data.get('score', 'N/A')}")
            print(f"  - Strength: {weak_data.get('strength', 'N/A')}")
        
        success, moderate_data = self.test_analyze_moderate_password()
        if success:
            print(f"  - Moderate password score: {moderate_data.get('score', 'N/A')}")
            print(f"  - Strength: {moderate_data.get('strength', 'N/A')}")
        
        success, strong_data = self.test_analyze_strong_password()
        if success:
            print(f"  - Strong password score: {strong_data.get('score', 'N/A')}")
            print(f"  - Strength: {strong_data.get('strength', 'N/A')}")
        
        self.test_analyze_common_password()
        self.test_analyze_pattern_password()
        self.test_analyze_unicode_password()
        self.test_analyze_very_long_password()
        
        # Print summary
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = PasswordStrengthAPITester()
    tester.run_all_tests()