import os
import json
import subprocess
import platform

def get_nba_player_analysis(player_name):
    try:
        # Point to the correct Node.js script
        script_path = os.path.join('yt webscraper puppeteer', 'index.js')
        
        # Create a temporary Node.js script that calls our main scraper
        with open('temp_script.js', 'w') as f:
            f.write(f'''
            const getPlayerAnalysis = require('./{script_path}');
            
            async function run() {{
                try {{
                    const analysis = await getPlayerAnalysis('{player_name}');
                    console.log(JSON.stringify(analysis));
                }} catch (error) {{
                    console.error(JSON.stringify({{error: error.message}}));
                }}
            }}
            
            run();
            ''')
        
        # Run the Node.js script
        result = subprocess.run(['node', 'temp_script.js'], 
                             capture_output=True, 
                             text=True,
                             cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Parse output
        try:
            if result.stderr:
                return {"error": result.stderr}
            return result.stdout.strip()
        except json.JSONDecodeError:
            return {"error": "Failed to parse Node.js output"}
            
    finally:
        # Clean up temp file
        if os.path.exists('temp_script.js'):
            os.remove('temp_script.js')