# Upload Media

Helper app in FLask for helping with storing files uploaded by users to a particular storage.

## SQLITE setup command

`python
from app import app, db
app.app_context().push()
db.create_all()
exit()`
