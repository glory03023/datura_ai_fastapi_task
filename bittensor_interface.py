import asyncio
from async_substrate_interface.async_substrate import AsyncSubstrateInterface
from bittensor.core.settings import SS58_FORMAT
from bittensor.core.chain_data import decode_account_id
from bittensor_wallet import Wallet
from redis_interface import get_redis_connection

async def get_tao_dividend_from_netuid_address(netuid, address):
    """
    Fetches the Tao dividend for a given address and netuid from either Redis cache
    or the blockchain. If the value is not cached, it queries the blockchain and
    stores the result in Redis for future use.
    
    Args:
        netuid (int): The network ID.
        address (str): The address whose Tao dividend is to be fetched.
    
    Returns:
        float: The Tao dividend value or None if it couldn't be fetched.
    """
    try:
        # Create a connection to Redis
        redis = await get_redis_connection()
        cache_key = f"tao_dividend:{netuid}:{address}"

        # Check if the Tao dividend is available in Redis cache
        cached_value = await redis.get(cache_key)
        if cached_value:
            print("Fetched from Redis cache")
            return float(cached_value)

        # If not cached, query the blockchain
        async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT) as substrate:
            block_hash = await substrate.get_chain_head()
            result = await substrate.query("SubtensorModule", "TaoDividendsPerSubnet", [netuid, address], block_hash=block_hash)

            # Cache the result in Redis for 120 seconds (2 minutes)
            if result:
                await redis.setex(cache_key, 120, result.value)
                return result.value

    except Exception as e:
        print(f"Error fetching Tao dividend: {e}")
        return None

    return None


async def get_tao_dividends_for_subnet(netuid):
    """
    Fetches the Tao dividends for all addresses under a particular netuid (subnet).
    It first checks Redis for cached values and if not found, queries the blockchain.

    Args:
        netuid (int): The network ID for which Tao dividends are to be fetched.

    Returns:
        list: A list of dictionaries mapping account IDs to their Tao dividends.
    """
    try:
        async def exhaust(qmr):
            """
            Helper function to exhaust the query map and return results as a list.

            Args:
                qmr (AsyncIterable): The async query map result to be iterated.

            Returns:
                list: A list of key-value pairs from the query map.
            """
            result = []
            async for k, v in await qmr:
                result.append((k, v))
            return result

        # Connect to Redis
        redis = await get_redis_connection()
        cache_key = f"tao_dividend:{netuid}"

        # Check if the value exists in Redis
        cached_value = await redis.get(cache_key)
        if cached_value:
            print("Fetched from Redis cache")
            return float(cached_value)

        # If not cached, query the blockchain
        async with AsyncSubstrateInterface("wss://entrypoint-finney.opentensor.ai:443", ss58_format=SS58_FORMAT) as substrate:
            block_hash = await substrate.get_chain_head()
            # Query the blockchain for Tao dividends for the subnet
            results = [substrate.query_map("SubtensorModule", "TaoDividendsPerSubnet", [netuid], block_hash=block_hash)]

            # Process the results to extract account IDs and their dividend values
            results = [exhaust(result) for result in results]
            results_dicts_list = []

            # Cache the results in Redis for 120 seconds (2 minutes)
            for future in asyncio.as_completed(results):
                result = await future
                results_dicts_list.extend([{decode_account_id(k): v.value} for k, v in result])

            return results_dicts_list

    except Exception as e:
        print(f"Error fetching Tao dividends for subnet {netuid}: {e}")
        return []

async def get_tao_dividends_for_address(address):
    """
    Fetches the Tao dividends for a given address across multiple netuids (1 to 50).
    It queries the blockchain for each netuid and returns the results.
    
    Args:
        address (str): The address whose Tao dividends are to be fetched across multiple subnets.

    Returns:
        list: A list of futures containing Tao dividend values from each subnet (netuid).
    """
    try:
        # Create a list of asynchronous tasks to get the Tao dividends for each netuid (1 to 50)
        results = [get_tao_dividend_from_netuid_address(i, address) for i in range(1, 51)]
        # Wait for all the tasks to complete
        return await asyncio.gather(*results)

    except Exception as e:
        print(f"Error fetching Tao dividends for address {address}: {e}")
        return []
