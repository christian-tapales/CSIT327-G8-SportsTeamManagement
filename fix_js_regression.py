
import os
import re

path = r'C:\Users\Matebook D14 BE\Desktop\CSIT327-G8-SportsTeamManagement\team_mgmt\templates\team_mgmt\team_detail.html'

if not os.path.exists(path):
    print("File not found")
    exit(1)

with open(path, 'rb') as f:
    content = f.read().decode('utf-8')

# Fix split currentCount
# Pattern: const currentCount = {{ players.count }<newline><whitespace>};
content = re.sub(r'const currentCount = \{\{ players\.count \}\s*\n\s*\};', 'const currentCount = {{ players.count }};', content)

# Also ensure team.status is definitely correct as I'm paranoid now
content = content.replace("team.status=='Active'", "team.status == 'Active'")
content = content.replace("team.status=='Inactive'", "team.status == 'Inactive'")

with open(path, 'wb') as f:
    f.write(content.encode('utf-8'))

print("Regression fixed.")
