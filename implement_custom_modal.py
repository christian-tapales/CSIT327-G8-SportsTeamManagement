
import os

path = r'C:\Users\Matebook D14 BE\Desktop\CSIT327-G8-SportsTeamManagement\team_mgmt\templates\team_mgmt\team_detail.html'

if not os.path.exists(path):
    print("File not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert the Custom Modal HTML
# We can find a good anchor point. "<!-- Custom Max Capacity Modal -->" doesn't exist yet.
# Let's insert it before <div id="editPlayerModal" ...
modal_html = """
    <!-- Custom Max Capacity Modal -->
    <div id="maxCapacityModal" class="hidden fixed inset-0 bg-black/60 z-50">
        <div class="min-h-full flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                <div class="flex items-start justify-between px-6 py-5 border-b">
                    <h3 class="text-xl font-semibold leading-6 text-gray-900">Limit Reached</h3>
                    <button id="closeMaxCapacityModal" class="text-gray-500 text-2xl">&times;</button>
                </div>
                <div class="px-6 py-6">
                    <p id="maxCapacityMessage" class="text-gray-600">
                        <!-- Message will be populated by JS -->
                    </p>
                    <div class="mt-6 flex justify-end">
                        <button id="okMaxCapacityModal" class="px-5 h-11 bg-gray-900 text-white rounded-xl hover:bg-black font-medium">OK</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
"""

# Check if already inserted (idempotency)
if 'id="maxCapacityModal"' not in content:
    # Insert before editPlayerModal
    anchor = '<div id="editPlayerModal"'
    if anchor in content:
        content = content.replace(anchor, modal_html + '\n\n    ' + anchor)
    else:
        print("Could not find anchor for modal insertion")
        exit(1)

# 2. Update JavaScript to use the modal
# We replace the specific event listener block or parts of it
# Old code pattern:
# if (maxCapacity > 0 && currentCount >= maxCapacity) {
#     alert("Cannot add more players. Team has reached max capacity of " + maxCapacity + ".");
# } else {

# New code pattern:
# if (maxCapacity > 0 && currentCount >= maxCapacity) {
#     if (maxCapacityMsg) {
#          maxCapacityMsg.textContent = "Cannot add more players. Team has reached max capacity of " + maxCapacity + ".";
#     }
#     if (maxCapacityModal) maxCapacityModal.classList.remove('hidden');
# } else {

# We also need to add the setupModal call and var definitions
# Let's find "setupModal('addPlayerModal', null, ['closeAddPlayerModal', 'cancelAddPlayerModal']);"
setup_anchor = "setupModal('addPlayerModal', null, ['closeAddPlayerModal', 'cancelAddPlayerModal']);"
setup_code = "\n            setupModal('maxCapacityModal', null, ['closeMaxCapacityModal', 'okMaxCapacityModal']);"

if setup_anchor in content and "setupModal('maxCapacityModal'" not in content:
    content = content.replace(setup_anchor, setup_anchor + setup_code)

# Add variable definitions
# Anchors: const addPlayerModal = document.getElementById('addPlayerModal');
var_anchor = "const addPlayerModal = document.getElementById('addPlayerModal');"
var_code = "\n            const maxCapacityModal = document.getElementById('maxCapacityModal');\n            const maxCapacityMsg = document.getElementById('maxCapacityMessage');"

if var_anchor in content and "const maxCapacityModal" not in content:
    content = content.replace(var_anchor, var_anchor + var_code)

# Replace the alert logic
# We need to be careful with whitespace matching.
# We'll construct a regex to match the alert block.
import re
# Match the if block containing the alert
pattern = r'if\s*\(maxCapacity\s*>\s*0\s*&&\s*currentCount\s*>=\s*maxCapacity\)\s*\{\s*alert\(.*?\);\s*\}\s*else\s*\{'
replacement = """if (maxCapacity > 0 && currentCount >= maxCapacity) {
                    if (maxCapacityMsg) {
                        maxCapacityMsg.textContent = "Cannot add more players. Team has reached max capacity of " + maxCapacity + ".";
                    }
                    if (maxCapacityModal) maxCapacityModal.classList.remove('hidden');
                } else {"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Custom modal implemented.")
