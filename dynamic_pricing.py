import pandas as pd

# Data: trucks going from Punjab to Rishikesh
data = {
    'OrderID': list(range(1, 11)),
    'Load_ton': [2, 5, 10, 3, 8, 12, 4, 6, 9, 7],
    'DeliveryUrgency': ['Standard', 'Express', 'Standard', 'Express', 'Standard', 'Express', 'Standard', 'Express', 'Standard', 'Express'],
    'TruckType': ['Mini Truck', 'Medium Truck', 'Heavy Truck', 'Mini Truck', 'Medium Truck', 'Heavy Truck', 'Mini Truck', 'Medium Truck', 'Heavy Truck', 'Medium Truck'],
    'CustomerType': ['Regular', 'Priority', 'Business', 'Priority', 'Business', 'Regular', 'Business', 'Priority', 'Regular', 'Business'],
    'BasePrice': [5000]*10
}

df = pd.DataFrame(data)

truck_multipliers = {
    'Mini Truck': 1.0,
    'Medium Truck': 1.3,
    'Heavy Truck': 1.6
}

def calculate_dynamic_price(row, peak_multiplier=1.15):
    base = row['BasePrice']
    load_charge = 800 * row['Load_ton']
    truck_mult = truck_multipliers[row['TruckType']]
    
    price = (base + load_charge) * truck_mult
    
    # Delivery urgency surcharge
    if row['DeliveryUrgency'] == 'Express':
        price *= 1.25  # 25% surcharge
    
    # Customer type adjustments
    if row['CustomerType'] == 'Priority':
        price *= 1.10  # 10% surcharge
    elif row['CustomerType'] == 'Business':
        price *= 0.95  # 5% discount
    
    # Peak demand multiplier
    price *= peak_multiplier
    
    return round(price, 2)

# Make sure this line is after function definition
df['DynamicPrice'] = df.apply(calculate_dynamic_price, axis=1)

print("Dynamic Pricing Output:")
print(df[['OrderID', 'Load_ton', 'DeliveryUrgency', 'TruckType', 'CustomerType', 'DynamicPrice']])
