# Homelessness Programs Simulation

*Original (Physical) Game developed by the National Association to End Homelessness (NAEH)*

*Virtual Simulation coded by jennifer lyden*

## Synopsis
This Simulation is designed to help communities understand how the homeless assistance system works. The simulation runs as a database-backed web app, allowing the user to make decisions about which programs to open, expand, and close.

## Set Up for Local Viewing
### On Host Machine
1. Install VirtualBox and Vagrant (see [Vagrant Setup](https://www.vagrantup.com/intro/getting-started/index.html)) and `init` a Linux environment (I used `ubuntu/trusty64`)
2. Add to **Vagrantfile**:
 * Port Forwarding: `config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"`
 * Folder Syncing (saves hassle of using Git inside virtual box): `config.vm.synced_folder "../relative/path/to/cloned/project/naeh-game/", "/game"`
3. Run Virtual Machine

### On Virtual Machine
1. Install Flask, SQLAlchemy, and MySQL
   * `sudo apt-get update && sudo apt-get upgrade`
   * `sudo apt-get install python3-pip`
   * `sudo -H pip3 install flask`
   * `sudo -H pip3 install flask-login`
   * `sudo -H pip3 install flask-sqlalchemy`
   * `sudo -H pip3 install flask-migrate`
   * `sudo -H pip3 install flask-script`
   * `sudo apt-get install mysql-server`
   * `sudo mysql_secure_installation`
   * `sudo -H pip3 install pymysql`
2. Install Yarn (package manager - see [Yarn Setup](https://yarnpkg.com/en/docs/install#linux-tab))
   * Install NodeJS 6
   `curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -`
   `sudo apt-get install -y nodejs`
   * Install Yarn
   `curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -`
   `echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list`
   `sudo apt-get update && sudo apt-get install yarn`
3. Setup Yarn and add dependencies
   * `cd /game`
   * `yarn init` - [complete form](https://yarnpkg.com/lang/en/docs/cli/init/)
   * `yarn add jquery@1.9.1`
   * `yarn add popper.js@^1.12.3`
   * `yarn add bootstrap@4.0.0-beta.2`
   * `yarn add chartjs`
4. Setup Database - if you change values, update config.py
   * Login to MySQL: `sudo mysql -u root -p`
   * `CREATE DATABASE naehgame CHARACTER SET UTF8;`
   * `CREATE USER naehgameuser@localhost IDENTIFIED BY '<password>';`
   * `GRANT ALL PRIVILEGES ON naehgame.* TO naehgameuser@localhost;`
   * `FLUSH PRIVILEGES;`
   * Logout of MySQL:`exit`
5. Migrate DB
   * `./manage.py db init`
   * `./manage.py db migrate`
   * `./manage.py db upgrade`



