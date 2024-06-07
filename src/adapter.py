import logging
import requests
import pandas as pd
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
secret = os.getenv("GRAPHQL_SECRET")

# set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# The Graph endpoint
SUBGRAPH_URL = f"https://subgraph.satsuma-prod.com/{secret}/metastreet-labs--232864/v2-pools-mainnet/api"


def fetch_tick_data(tick_id):
    """
    Fetch tick data for a given tick id
    """

    # Define the GraphQL query
    query = """
    query($tickId: String!){
       tick(id: $tickId){
        raw
        redemptionPending
        pool {
          id
        }
      }
    }
    """

    # Define the variables for the query
    variables = {
        "tickId": tick_id
    }

    # Make the HTTP request to the GraphQL endpoint
    response = requests.post(
        SUBGRAPH_URL,
        json={'query': query, 'variables': variables}
    )


    # Check for errors in the response
    if response.status_code == 200:
        # Parse the JSON response
        print(response.text)
        data = response.json()

        return data["data"]["tick"]["raw"], data["data"]["tick"]["pool"]["id"], data["data"]["tick"]["redemptionPending"]
    else:
        # Handle errors
        logging.error(f"Query failed with status code {response.status_code}")
        logging.error(response.text)

        raise Exception(f"Query failed with status code {response.status_code}")



def fetch_tick_loans(pool_id, tick_raw):
    """
    Fetch loans for a given pool and tick (raw)
    """

    # Define the GraphQL query
    query = """
    query($pool: String!, $tick: String!) {
      loans(
        where: { pool: $pool, ticks_contains: [$tick], status: Active }
        orderBy: maturity
        orderDirection: asc
      ) {
        id
        collateralToken {
          id
          name
        }
    	  collateralTokenIds
      }
    }
    """

    # Define the variables for the query
    variables = {
        "pool": pool_id,
        "tick": tick_raw
    }

    # Make the HTTP request to the GraphQL endpoint
    response = requests.post(
        SUBGRAPH_URL,
        json={'query': query, 'variables': variables}
    )


    # Check for errors in the response
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        return data["data"]["loans"]
    else:
        # Handle errors
        logging.error(f"Query failed with status code {response.status_code}")
        logging.error(response.text)
        raise Exception(f"Query failed with status code {response.status_code}")


def main():
    parser = argparse.ArgumentParser(description="Retrieves tick data for a give tick id.")
    parser.add_argument('--tick', type=str, help='The tick id to retrieve data for (required)', required=True)
    args = parser.parse_args()

    tick_id = args.tick

    logging.info(f'Retrieving data for {tick_id} from "{SUBGRAPH_URL}"')

    # Get the tick data
    raw, pool, pending = fetch_tick_data(tick_id)

    # Get the loans
    loans = fetch_tick_loans(pool, raw)

    # Prepare the data for the CSV file
    data = []
    for loan in loans:
        # if it's too big we can stream it to a file
        for token_id in loan["collateralTokenIds"]:
          data.append({
              "pool_id": pool,
              "redemption_pending": pending,
              "loan_id": loan["id"],
              "collection_contract": loan["collateralToken"]["id"],
              "collection_name": loan["collateralToken"]["name"],
              "token": token_id
          })
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Write the DataFrame to a CSV file
    df.to_csv("output.csv", index=False)

    logging.info(f'Exported {len(df)} records to "output.csv"')

if __name__ == "__main__":
    main()
