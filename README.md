# dependency parsetree
## Linux installation and execution
### Installation
Install python 3 on your sistem. 

Run the following commands in terminal:
```bash
cd <PATH TO PROJECT DIRECTORY>
pip3 install -r requirements.txt
```

### Execution
Set up search parameters in `.ini` file.

Execute extraction by first moving to project directory with:
```bash
cd <PATH TO PROJECT DIRECTORY>
```

And later executing script with:
```bash
python3 dependency-parsetree.py --config_file=<PATH TO .ini file>
```

Example:
```bash
python3 dependency-parsetree.py --config_file=official_config.ini
```
