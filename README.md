
Dev loop
```
   $ ./loop-docker
```

After changing the database schema
```
   $ touch rm-vol
   $ docker-compose-down
```

To add a column

* add to schema
* do schema change dance above
* add to column map in loader
* add to query
