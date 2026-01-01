"""
API Cost Controller - Automatic Protection Against Overspending
Prevents unexpected billing charges by enforcing daily/monthly limits
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

class APICostController:
    def __init__(
        self, 
        daily_limit: int = 2000,
        monthly_budget_inr: float = 500.0,
        cost_per_request: float = 0.0125  # ₹0.0125 per request (approx)
    ):
        self.daily_limit = daily_limit
        self.monthly_budget = monthly_budget_inr
        self.cost_per_request = cost_per_request
        self.usage_file = "api_usage_tracker.json"
        self.usage = self._load_usage()
    
    def _load_usage(self) -> Dict[str, Any]:
        """Load usage data from file"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                    # Reset if new day/month
                    data = self._check_reset(data)
                    return data
            except:
                pass
        
        return self._create_new_usage()
    
    def _create_new_usage(self) -> Dict[str, Any]:
        """Create new usage tracker"""
        now = datetime.now()
        return {
            "today": {
                "date": now.strftime("%Y-%m-%d"),
                "count": 0,
                "estimated_cost": 0.0
            },
            "month": {
                "month": now.strftime("%Y-%m"),
                "count": 0,
                "estimated_cost": 0.0
            },
            "total": {
                "all_time_requests": 0,
                "all_time_cost": 0.0
            }
        }
    
    def _check_reset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reset counters if new day/month"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        this_month = now.strftime("%Y-%m")
        
        # Reset daily counter
        if data.get("today", {}).get("date") != today:
            data["today"] = {
                "date": today,
                "count": 0,
                "estimated_cost": 0.0
            }
        
        # Reset monthly counter
        if data.get("month", {}).get("month") != this_month:
            data["month"] = {
                "month": this_month,
                "count": 0,
                "estimated_cost": 0.0
            }
        
        return data
    
    def _save_usage(self):
        """Save usage data to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving usage data: {e}")
    
    def can_make_request(self) -> tuple[bool, str]:
        """
        Check if request is allowed based on limits
        Returns: (allowed: bool, reason: str)
        """
        # Check daily limit
        if self.usage["today"]["count"] >= self.daily_limit:
            return False, f"❌ Daily limit reached ({self.daily_limit} requests). Try tomorrow."
        
        # Check monthly budget
        monthly_cost = self.usage["month"]["estimated_cost"]
        if monthly_cost >= self.monthly_budget:
            return False, f"❌ Monthly budget exceeded (₹{monthly_cost:.2f}/₹{self.monthly_budget}). Wait for next month."
        
        # Check if next request will exceed monthly budget
        next_cost = monthly_cost + self.cost_per_request
        if next_cost > self.monthly_budget:
            return False, f"❌ Next request will exceed monthly budget (₹{next_cost:.2f}/₹{self.monthly_budget})"
        
        return True, "✅ Request allowed"
    
    def record_request(self):
        """Record an API request"""
        # Increment counters
        self.usage["today"]["count"] += 1
        self.usage["today"]["estimated_cost"] += self.cost_per_request
        
        self.usage["month"]["count"] += 1
        self.usage["month"]["estimated_cost"] += self.cost_per_request
        
        self.usage["total"]["all_time_requests"] += 1
        self.usage["total"]["all_time_cost"] += self.cost_per_request
        
        # Save to file
        self._save_usage()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        daily_remaining = self.daily_limit - self.usage["today"]["count"]
        monthly_remaining = self.monthly_budget - self.usage["month"]["estimated_cost"]
        
        return {
            "today": {
                "requests": self.usage["today"]["count"],
                "limit": self.daily_limit,
                "remaining": daily_remaining,
                "cost": f"₹{self.usage['today']['estimated_cost']:.2f}"
            },
            "month": {
                "requests": self.usage["month"]["count"],
                "budget": f"₹{self.monthly_budget}",
                "spent": f"₹{self.usage['month']['estimated_cost']:.2f}",
                "remaining": f"₹{monthly_remaining:.2f}"
            },
            "total": {
                "all_time_requests": self.usage["total"]["all_time_requests"],
                "all_time_cost": f"₹{self.usage['total']['all_time_cost']:.2f}"
            }
        }
    
    def reset_daily(self):
        """Manually reset daily counter"""
        self.usage["today"]["count"] = 0
        self.usage["today"]["estimated_cost"] = 0.0
        self._save_usage()
        print("✅ Daily counter reset")
    
    def reset_monthly(self):
        """Manually reset monthly counter"""
        self.usage["month"]["count"] = 0
        self.usage["month"]["estimated_cost"] = 0.0
        self._save_usage()
        print("✅ Monthly counter reset")

# Global instance
cost_controller = APICostController(
    daily_limit=2000,           # Max 2000 requests per day
    monthly_budget_inr=500.0    # Max ₹500 per month
)

def check_api_limit() -> tuple[bool, str]:
    """Check if API request is allowed"""
    return cost_controller.can_make_request()

def record_api_call():
    """Record an API call"""
    cost_controller.record_request()

def get_usage_stats() -> Dict[str, Any]:
    """Get current usage statistics"""
    return cost_controller.get_stats()

def print_usage_stats():
    """Print usage statistics in readable format"""
    stats = get_usage_stats()
    
    print("\n" + "="*50)
    print("📊 API USAGE STATISTICS")
    print("="*50)
    
    print(f"\n📅 TODAY ({stats['today']['requests']}/{stats['today']['limit']} requests)")
    print(f"   Remaining: {stats['today']['remaining']} requests")
    print(f"   Cost: {stats['today']['cost']}")
    
    print(f"\n📆 THIS MONTH")
    print(f"   Requests: {stats['month']['requests']}")
    print(f"   Spent: {stats['month']['spent']} / {stats['month']['budget']}")
    print(f"   Remaining: {stats['month']['remaining']}")
    
    print(f"\n🌍 ALL TIME")
    print(f"   Total Requests: {stats['total']['all_time_requests']}")
    print(f"   Total Cost: {stats['total']['all_time_cost']}")
    
    print("="*50 + "\n")

# Example usage
if __name__ == "__main__":
    print_usage_stats()
    
    # Test limit check
    allowed, reason = check_api_limit()
    print(f"\n{reason}")
    
    if allowed:
        record_api_call()
        print("✅ API call recorded")
        print_usage_stats()
