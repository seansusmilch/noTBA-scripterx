# This script tests the threadsafe-ness of the database.
# With many processes accessing the database, the database should
# be able to handle all incoming operations to keep the data intact.

# collection of ids known to need either a title or a thumbnail
$collection = 60289,80683,60288,1210,1204,21173,21166,21169,21168,21174
foreach ($item in $collection) {
    Write-Output "Starting check for : $item"
    Start-Process python "./checkEp.py Episode $item false"
}
$collection.Count
python -c "
from helpers import get_db
db = get_db()
print(len(list(db.keys())))
"