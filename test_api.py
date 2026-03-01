"""Test script to explore PyKappa API"""

from pykappa.system import System

system = System.from_ka(
    """
    %init: 100 A(x[.])
    %init: 100 B(x[.])

    %obs: 'AB' |A(x[1]), B(x[1])|

    A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ 1, 1
    """
)

# Run a few updates
for _ in range(5):
    system.update()

print("System attributes:")
print(dir(system))
print("\nMonitor attributes:")
print(dir(system.monitor))
print("\nMixture attributes:")
print(dir(system.mixture))

print("\nSystem type:", type(system))
print("Monitor type:", type(system.monitor))
print("Mixture type:", type(system.mixture))

# Try to access monitor data
print("\n=== Trying different ways to access monitor ===")
print("system.monitor:", system.monitor)

# Check if it has __getitem__
if hasattr(system.monitor, '__getitem__'):
    print("Monitor is subscriptable")
else:
    print("Monitor is NOT subscriptable")

# Check for common attributes
for attr in ['data', 'observables', 'values', 'history', 'records', 'get', '__dict__']:
    if hasattr(system.monitor, attr):
        print(f"system.monitor.{attr}:", getattr(system.monitor, attr))

# Test accessing AB observable
print("\n=== Testing observable access ===")
print("system.monitor.history['AB']:", system.monitor.history['AB'])
print("Current AB value:", system.monitor.history['AB'][-1])

# Test if system has __getitem__
print("\n=== Testing system[...] access ===")
try:
    print("system['AB']:", system['AB'])
except Exception as e:
    print(f"Error accessing system['AB']: {e}")

# Test mixture query
print("\n=== Testing mixture query ===")
try:
    # Look for a query or select method
    if hasattr(system.mixture, 'select'):
        print("Mixture has select method")
    if hasattr(system.mixture, 'query'):
        print("Mixture has query method")

    # Try counting agents
    print("Number of agents:", len(list(system.mixture.agents)))
except Exception as e:
    print(f"Error: {e}")
