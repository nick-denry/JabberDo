# TODO over XMPP

Pros. Easy share your task lists with any device since jabber clients are everywhere.

**Disclaimer:** This is pre-alpha software. Everything could be changed. Follow README to watch the changes. 

## 1. Command list

**Diplay Help:**

Just text `?`

**Control lists:**

`..` - output existing lists  
`.list_name` - add or display list, i.e. `.tasks`. Also makes list "active".  
`.` - display active list  
`.--` - clear tasks of the active list  
`.!` - display completed tasks of the active list  
`.!-` - clear completed tasks of the active list  
`.-list_name` - delete list and all of its tasks     

**Control tasks:**
    
`any message` - adds task to the active list    
`:any multiline message` - add multiple tasks from multiline message  
`!task_number` - move task `task_number` to complete tasks    
`-task_number` - delete task `task_number` from list, i.e. -1 deletes first task.
`>task_number task_title` - edit task `task_number` from current list, set it new `title`  
`^task_number list_name` - move task `task_number` from current list to `list_name` list    

**Schedule tasks:**

`*task_number time` or `*task_number date time` - set reminder for task `task_number` from active list to provided time or date/time
    
    example: *1 22:04 - set reminder for task 1 from active list to 22:04 today.

`.*` - list scheduled tasks
       
 

## 2. Requremens

- Redis server
- [SleekXMPP](https://github.com/fritzy/SleekXMPP)
- python-redis
- python-yaml
- python-dateutil

## 3. Installation

1. Create `virtualenv` in your preferred way.

#### Debian/Ubuntu example.

    sudo apt-get install redis-server  # Install redis server
    sudo apt-get install python3-pip  # Install python3-pip
    sudo pip3 install virtualenv  # Install virtualenv 
    virtualenv -p python3 myenv  # Create virtualenv
    source myenv  # Activate created env
    # Add packages
    pip3 install sleekxmpp
    pip3 install redis
    pip3 install pyyaml
    pip3 install python-dateutil
    deactivate  # Deactivate env
    
 

2. [Download bot files](https://github.com/nick-denry/PyXmmpDo/archive/master.zip) or clone form github:
```bash
git clone https://github.com/nick-denry/PyXmmpDo.git 
```

2. Copy `main-local.dist.yml` to `main-local.yml` at `config` folder.

```bash
cp main-local.dist.yml main-local.yml
```

Set config as follow:

```yaml
bot_account:
  jid: bot_jid@example.com
  password: bot_password
  port: 5222
  PROTOCOL_SSLv23: True

db:
  type: redis

redis_db:
  host: localhost
  port: 6379
  db: 0

allowed_jids:
  - jid@example.com
 ```
 
 `allowed_jids` - users allowed to interact with bot.

## 4. Run

Run in background with `screen` and created environment

```bash
screen myenv/bin/python3 bot.py 
```
