# Record to accesses

Record to accesses at social website.

## Getting Started

### Prerequisites

Installed the following program.

- Python3.x
- ChromeDriver

Setup the AWS services.

- API Gateway (`GET` and `PUT` endpoint)
- Lambda (Refer at `lambda` directory)
- DynamoDB (Table name is `access_to_socials`, primary key is `date_of_access`)

### Installing

Execute command at cloned directory root.

```
cd <project_dir>

python -m venv venv

# Mac/Linux
./venv/bin/activate

# Windows
venv\Scripts\activate.bat

pip install -r requirements.txt
```
