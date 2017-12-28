# Record to accesses

Record to accesses at social website.

## Getting Started

### Prerequisites

Installed the following program.

- Python3.x
- pipenv
- ChromeDriver

Setup the AWS services.

- API Gateway (`GET` and `PUT` endpoint)
- Lambda (Refer at `lambda` directory)
- DynamoDB (Table name is `access_to_socials`, primary key is `date_of_access`)

Copy `.env.example` to `.env`, changes using local value.

### Installing

Execute command at cloned directory root.

```
$ cd <project_dir>
$ pipenv install
```

### Run

```
$ pipenv run python main.py
```
