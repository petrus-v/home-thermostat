* launch states

pyinfra inventories/prod.py operations/deploy.py 

* compute data inventory

pyinfra inventories/prod.py debug-inventory -vv

* get server facts

pyinfra inventories/prod.py all-facts

