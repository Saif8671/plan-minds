import os
import re
from pathlib import Path

ROUTERS_DIR = Path("e:/saif/projects made/building/app/backend/app/api")

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements for schemas
    content = content.replace("from app.schemas.auth import MessageResponse", "from app.schemas.base import MessageData")
    content = content.replace("from app.schemas.auth import PaginatedResponse", "from app.schemas.base import PaginatedData")
    
    # Handle response_model replacements
    # response_model=SomeModel -> response_model=ApiResponse[SomeModel]
    # We have to be careful not to replace it if it's already ApiResponse
    
    # We will use AST to properly rewrite this if needed, but for now we can just do a regex replace
    # pattern: response_model=([A-Za-z0-9_]+)
    def repl_response_model(match):
        model = match.group(1)
        if model.startswith("ApiResponse") or model == "None":
            return match.group(0)
        return f"response_model=ApiResponse[{model}]"
    
    content = re.sub(r'response_model=([A-Za-z0-9_]+(?:\[[A-Za-z0-9_]+\])?)', repl_response_model, content)

    # Convert returns
    # return await ... -> result = await ...\n    return ApiResponse(data=result)
    # return SomeModel(...) -> return ApiResponse(data=SomeModel(...))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk(ROUTERS_DIR):
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))

print("Done")
