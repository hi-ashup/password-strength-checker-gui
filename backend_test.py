import requests
import unittest
import json

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