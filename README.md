# backup-sync
Synchronization for a backup directory.

```
Usage: backup_sync.py <src dir> <backup dir>
```

Notes:
- Use python 3, otherwise you might get 'buffer overflow' errors during the directory iteration.
- Currently doesn't support file renaming, and a renamed file will be handled as a new file.

Enjoy!