import requests
import json

# The new Goldsky Activity API
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"

def diagnose_api():
    print(f"🕵️  Inspecting API Schema at: {GRAPH_URL}")
    print("-" * 60)

    # 1. Introspection Query (Asks "What tables exist?")
    query = """
    {
      __schema {
        types {
          name
          description
        }
      }
    }
    """
    
    try:
        response = requests.post(GRAPH_URL, json={'query': query}, timeout=10)
        if response.status_code != 200:
            print(f"❌ Connection Failed: Status {response.status_code}")
            return

        data = response.json()
        types = data.get('data', {}).get('__schema', {}).get('types', [])
        
        # Filter for likely table names (ignoring system types)
        tables = [t['name'] for t in types if not t['name'].startswith('__') and not t['name'].endswith('Payload')]
        
        print("✅ CONNECTION SUCCESS! Found these tables:")
        print(tables)
        
        # 2. Try to guess the right table
        print("\n🧪 Testing common table names...")
        candidates = ['globalDeals', 'trades', 'transactions', 'activities', 'actions', 'fills']
        
        for table in candidates:
            if table in tables:
                print(f"   PLEASE USE THIS -> Found table: '{table}'")
            # If standard names fail, we look at the list printed above.

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    diagnose_api()
