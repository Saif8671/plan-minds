import asyncio
import httpx
import os
import subprocess
import time

async def run():
    # Make sure we unset ENVIRONMENT
    env = os.environ.copy()
    if "ENVIRONMENT" in env:
        del env["ENVIRONMENT"]
    
    # Start server
    proc = subprocess.Popen(["python", "-m", "uvicorn", "main:app", "--port", "8008"], env=env)
    print("Started server on port 8008...")
    time.sleep(3)  # wait for startup
    
    try:
        async with httpx.AsyncClient(base_url="http://localhost:8008") as client:
            print("================ ITEM 2 ================")
            email = "realuser@example.com"
            # Register user
            await client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!", "name": "Real User"})
            
            # Call forgot password
            resp = await client.post("/api/v1/auth/forgot-password", json={"email": email})
            print(f"Forgot password status ({resp.status_code}): {resp.json()}")
            
            print("\n================ ITEM 3 ================")
            # Now test redis down
            # Actually we can't easily shut down redis from python. 
            # We can start the server with a bad redis URL
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    asyncio.run(run())
