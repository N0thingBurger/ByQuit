from pybit.unified_trading import HTTP
import time

# --- CONFIGURATION ---
# REPLACE THESE WITH YOUR NEW KEYS
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"
USE_TESTNET = False  # Set to False for real trading

# Initialize the session
session = HTTP(
    testnet=USE_TESTNET,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

def get_active_positions():
    """
    Fetches all open positions (Linear USDT Perpetual).
    Returns a list of position dictionaries.
    """
    try:
        response = session.get_positions(category="linear", settleCoin="USDT")
        positions = response.get('result', {}).get('list', [])
        # Filter for positions that actually have a size > 0
        active_positions = [p for p in positions if float(p['size']) > 0]
        return active_positions
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []

def show_positions(positions):
    """
    Prints positions with an ID number for selection.
    """
    if not positions:
        print("No open positions found.")
        return

    print(f"\n{'ID':<5} {'SYMBOL':<15} {'SIDE':<10} {'SIZE':<10} {'ENTRY PRICE':<15} {'PNL':<15}")
    print("-" * 75)

    # Enumerate gives us an index (0, 1, 2...) which we use as the ID (1, 2, 3...)
    for i, p in enumerate(positions):
        symbol = p['symbol']
        side = p['side']
        size = p['size']
        entry_price = p['avgPrice']
        pnl = p['unrealisedPnl']

        print(f"{i+1:<5} {symbol:<15} {side:<10} {size:<10} {entry_price:<15} {pnl:<15}")
    print("-" * 75)

def close_target_position(p):
    """
    Closes a SINGLE specific position passed to it.
    """
    symbol = p['symbol']
    side = p['side']
    size = p['size']
    position_idx = p['positionIdx']

    # Determine opposite side
    close_side = "Sell" if side == "Buy" else "Buy"

    try:
        print(f"Closing {symbol} ({side}, Size: {size})...")

        session.place_order(
            category="linear",
            symbol=symbol,
            side=close_side,
            orderType="Market",
            qty=size,
            positionIdx=position_idx,
            reduceOnly=True,
            timeInForce="GTC"
        )
        print(f"✅ Successfully market closed {symbol}.")
        return True
    except Exception as e:
        print(f"❌ Failed to close {symbol}: {e}")
        return False

if __name__ == "__main__":
    # 1. Get Positions
    print("Fetching active positions...")
    active_positions = get_active_positions()

    # 2. Show Positions with IDs
    show_positions(active_positions)

    # 3. Selection Logic
    if active_positions:
        print("\n--- OPTIONS ---")
        print("Type the [ID] number to close a specific position (e.g., 1)")
        print("Type 'ALL' to close EVERYTHING.")
        print("Type 'Q' to quit.")

        user_input = input("\nYour choice: ").strip().upper()

        if user_input == "ALL":
            # Close everything
            for p in active_positions:
                close_target_position(p)
                time.sleep(0.1) # Rate limit safety

        elif user_input.isdigit():
            # Close specific position
            selection_index = int(user_input) - 1 # Convert ID 1 to Index 0

            if 0 <= selection_index < len(active_positions):
                target_position = active_positions[selection_index]
                close_target_position(target_position)
            else:
                print("❌ Invalid ID selected.")

        elif user_input == 'Q':
            print("Exiting...")
        else:
            print("Invalid input.")

        # 4. Verify results
        print("\nVerifying remaining positions...")
        remaining = get_active_positions()
        show_positions(remaining)
