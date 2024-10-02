# Importing the re module
import re

# Given string
s = "I am a human being."

# Performing the Sub() operation
res_1 = re.sub('a', 'x', s)
res_2 = re.sub('[a,I]','x',s)

# Print results
print(res_1)
print(res_2)

# The original string remains unchanged
print(s)