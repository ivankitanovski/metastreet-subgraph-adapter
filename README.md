# MetaStreet Subgraph Adapter

This adapter retrieves tick data for a given tick ID and exports the related loan data to a CSV file. 

## Setup

Before running the script, ensure you have the following installed:

- Python 3.x
- `requests` library
- `pandas` library
- `pythdon-dotenv` library

Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

To retrieve all snapshots and save them to a CSV file, run the script without with the `--tick` argument

```bash
python src/adapter.py --tick=<TICK_ID>
```

## Directory Structure

metastreet-subgraph-adapter/    
├── src/  
│ └── adapter.py  
├── output.csv  
├── requirements.txt  
└── README.md  

