# MySQL School Project

[فارسی](README.fa.md)

A small terminal CRUD application (Python) that talks to a **MySQL 8.4 server running on a separate Linux machine**. The goal of this project is not the app itself, but to show how to set up and connect to a remote database **securely**, and to explain the reason behind every security decision.

## Architecture

```
 Windows (client)                                   Kubuntu 26.04 VM (server)
 ┌──────────────────────┐                          ┌─────────────────────────────┐
 │ app.py (Python)      │      TCP 3306            │ ufw firewall                │
 │ mysql-connector      │ ───────────────────────► │  allow only 192.168.35.1    │
 │ .env (secrets)       │   VMware NAT (VMnet8)    │ MySQL 8.4                   │
 │ 192.168.35.1         │                          │  bind-address 192.168.35.128│
 └──────────────────────┘                          │  user school_app@192.168.35.1│
                                                   └─────────────────────────────┘
```

| Machine | Role | IP (private, VMware NAT) |
|---|---|---|
| Windows host | Client: code, Git, Python | `192.168.35.1` |
| Kubuntu VM | Server: MySQL only | `192.168.35.128` |

A connection must pass four checks, in this order. Each check is independent:

1. **Firewall (ufw):** is the packet from an allowed IP to the allowed port?
2. **Network binding (`bind-address`):** is MySQL listening on this network interface?
3. **Identity:** does a user exist for this name *and* this client host, with this password?
4. **Privileges (`GRANT`):** is this user allowed to run this statement on this database?

## Security decisions

| Decision | Why | Without it |
|---|---|---|
| `bind-address` = the server's own IP | MySQL listens on one interface only | `0.0.0.0` makes MySQL listen on every interface of the server |
| `mysqlx-bind-address` = `127.0.0.1` | The X protocol port is not needed, so it stays internal | An unused service exposed to the network |
| User `school_app@'192.168.35.1'` | Identity is tied to the client machine | `'%'` lets any host try to log in |
| `ufw allow from <client IP> to any port 3306 proto tcp` | Only one client can reach the port | An open port invites brute-force attempts from the whole network |
| `GRANT SELECT, INSERT, UPDATE, DELETE` on one database | Least privilege | A bug or SQL injection could `DROP` tables or touch other databases |
| `.env` listed in `.gitignore`, `.env.example` committed | Secrets stay out of Git history, but the template is shared | A leaked password stays in history forever and must be rotated |
| `%s` placeholders in all queries | Parameterized queries | SQL injection |
| Root uses `auth_socket`, admin work done with `sudo mysql` | No root password to steal over the network | A remotely usable root account |
| `mysql_secure_installation` with password validation (MEDIUM) | Weak passwords are rejected | Easy-to-guess passwords |
| `ufw allow ssh` before enabling the firewall | Avoid locking yourself out of a remote server | Lost access to the server |

**Defense in depth:** if one layer is weakened, the others still limit the damage. For example, even if the firewall were opened to everyone, a stranger would still be rejected by the identity layer (error 1045).

## Reading connection errors

| Error | Meaning | Layer |
|---|---|---|
| `2003 Can't connect to MySQL server` | The door was not found or was closed | Firewall / `bind-address` / MySQL not running |
| `1045 Access denied for user` | The door opened, but entry was refused | Identity (wrong user, host or password) |
| `1142 command denied` | Logged in, but this statement is not allowed | Privileges (`GRANT`) |
| `1062 Duplicate entry` | A `UNIQUE` constraint rejected the row | Data (not a security error) |

## Setup

### 1. Server (Kubuntu), run in a terminal

```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

Make MySQL listen only on the server's own IP. Back up the file first, then edit it:

```bash
sudo cp /etc/mysql/mysql.conf.d/mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf.bak
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

```ini
bind-address         = <SERVER_IP>
mysqlx-bind-address  = 127.0.0.1
```

```bash
sudo systemctl restart mysql
sudo systemctl enable mysql
sudo ss -tlnp | grep 3306        # should show <SERVER_IP>:3306
```

Create the database and the restricted user (choose your own strong password, and never commit it):

```bash
sudo mysql < schema.sql
sudo mysql
```

```sql
CREATE USER 'school_app'@'<CLIENT_IP>' IDENTIFIED BY '<strong-password>';
GRANT SELECT, INSERT, UPDATE, DELETE ON school_db.* TO 'school_app'@'<CLIENT_IP>';
SHOW GRANTS FOR 'school_app'@'<CLIENT_IP>';
```

Firewall, open only for the client:

```bash
sudo ufw allow ssh
sudo ufw allow from <CLIENT_IP> to any port 3306 proto tcp
sudo ufw enable
sudo ufw status numbered
```

### 2. Client (Windows, CMD)

```
git clone <this-repository-url>
cd mysql-school-project
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and fill in the real values (especially `DB_PASSWORD`). This file is ignored by Git.

```
python app.py
```

## Project structure

```
mysql-school-project/
├── README.md          English documentation
├── README.fa.md       Persian documentation
├── .gitignore         Keeps .env, venv and IDE files out of Git
├── .env.example       Template of required settings (no secrets)
├── schema.sql         Database and table definition (no passwords)
├── app.py             Terminal CRUD menu for the students table
└── requirements.txt   Python dependencies
```

## What I learned

- A connection passes through several independent layers, and error codes (2003 vs 1045 vs 1142) tell you which layer rejected it.
- In MySQL, identity is **user + host**. `school_app@localhost` and `school_app@'192.168.35.1'` are two different accounts.
- `bind-address` belongs to the **server** (where to listen); the user's host belongs to the **client** (who may log in).
- Least privilege limits the damage of bugs and injection.
- Git keeps history forever, so a leaked secret must be treated as compromised and rotated, not just deleted.
- Dynamic IPs can break `bind-address`; for a longer-lived setup the server IP should be made static.
