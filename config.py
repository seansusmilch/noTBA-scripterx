api_token = ''
base_url = ''

# Different Logging Levels
#     4: DEBUG
#     3: INFO
#     2: WARNING (recommended)
#     1: ERROR
#     0: CRITICAL
logging_level = 2

# Time in seconds to wait before rechecking title after refreshing metadata
recheck_wait_time = 1

# Number of days to refresh an episode before giving up on it
days_before_giving_up = 10

# The limit of the number concurrent requests to run. 
# This applies to checkAllEps.py and refreshEps.py
limit_concurrent_requests = 8

# Set to true if you want to check for placeholder thumbnails.
check_thumbs = False