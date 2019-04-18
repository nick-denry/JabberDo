# TODO over XMPP

Pros. Easy share your task lists with any device since jabber clients are everywhere.


## 1. Command list

**Diplay Help:**

Just type `?`

**Control lists:**

`..` - output existing lists  
`.<list_name>` - add or display list, i.e. `.tasks`. Also makes list "active".  
`.` or `.*` - display active list  
`.*-` - clear tasks of the active list
`.!` - display completed tasks of the active list  
`.!-` - clear completed tasks of the active list  
`.-<list_name>` - delete list and all of its tasks     

**Control tasks:**
    
Any message - adds task to the active list  
`!<number` - move task to completed    
`-<number>` - delete task `<number>` from list, i.e. -1 deletes first task.  
 

## 2. Requremens

- Redis server
- [SleekXMPP](https://github.com/fritzy/SleekXMPP)
- python-redis
- python-yaml

## 3. Installation

1. [Download bot files](https://github.com/nick-denry/PyXmmpDo/archive/master.zip) or clone form github:
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

Run in background with `nohup`

```bash
nohup python bot.py >/dev/null 2>&1 
```
