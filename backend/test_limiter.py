from app.core.rate_limit import limiter
from app.core.config import get_settings

def test_rate_limiter():
    print("Testing limiter initialization...")
    print(limiter)
    
if __name__ == "__main__":
    test_rate_limiter()
