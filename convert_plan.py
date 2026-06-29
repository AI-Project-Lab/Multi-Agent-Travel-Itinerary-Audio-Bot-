import markdown
import os

input_path = r"c:\Users\raksh\.gemini\antigravity\brain\1f80cdc3-a767-497d-a04b-52bd4ca4cb15\workshop_plan.md"
output_path = r"c:\Users\raksh\.gemini\antigravity\brain\1f80cdc3-a767-497d-a04b-52bd4ca4cb15\workshop_plan.html"

with open(input_path, "r", encoding="utf-8") as f:
    text = f.read()

html_body = markdown.markdown(text, extensions=['fenced_code', 'tables'])

html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        max-width: 850px; 
        margin: 40px auto; 
        padding: 20px; 
        line-height: 1.6; 
        color: #333;
    }}
    h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
    h2 {{ color: #34495e; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
    h3 {{ color: #16a085; margin-top: 25px; }}
    code {{ 
        background-color: #f8f9fa; 
        padding: 2px 6px; 
        border-radius: 4px; 
        font-family: Consolas, 'Courier New', monospace; 
        color: #e74c3c;
    }}
    pre {{ 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 6px; 
        overflow-x: auto; 
        border: 1px solid #e9ecef;
    }}
    pre code {{ 
        background-color: transparent; 
        padding: 0; 
        color: #333;
    }}
    blockquote {{
        border-left: 4px solid #1abc9c;
        margin: 0;
        padding-left: 15px;
        color: #555;
    }}
    @media print {{
        body {{ max-width: 100%; margin: 0; padding: 20px; }}
        a {{ text-decoration: none; color: #000; }}
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully converted {input_path} to {output_path}")
