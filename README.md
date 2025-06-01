# simple-forum

A simple forum web application build with flask and bootstrap.

Default credentials: `admin:admin`

![](img/home.png)

![](img/thread.png)

## Docker

````shell
docker build -t simple_forum .
docker run --name simple_forum -d -p 8000:5000 -t simple_forum:latest
````

## Features

- Markdown support
- Create threads
- Create, read, edit, delete and report posts
- Profile page with avatar
- Admin dashboard
- Pagination
