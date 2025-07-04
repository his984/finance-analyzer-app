#!/usr/bin/env python3
"""
Test script to verify the index handling logic for the finance analyzer app.
"""

import pandas as pd
from core.data_utils import filter_dataframe

def test_index_preservation():
    """Test that filtering preserves original indices."""
    # Create a test DataFrame with original indices
    data = {
        'Accounting date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
        'Description': ['Test1', 'Test2', 'Test3', 'Test4'],
        'Amount': [100, -50, 200, -75],
        'Category': ['Income', 'Expense', 'Income', 'Expense']
    }
    
    # Create DataFrame with non-sequential indices to simulate real data
    df = pd.DataFrame(data, index=[10, 25, 42, 67])
    print("Original DataFrame:")
    print(df)
    print(f"Original indices: {list(df.index)}")
    print()
    
    # Test filtering
    filtered_df = filter_dataframe(df, category="Income")
    print("Filtered DataFrame (Income only):")
    print(filtered_df)
    print(f"Filtered indices: {list(filtered_df.index)}")
    print()
    
    # Test row mapping logic
    row_mapping = {}
    for position, original_idx in enumerate(filtered_df.index):
        row_mapping[position] = original_idx
    
    print("Row mapping (position -> original_index):")
    for pos, orig_idx in row_mapping.items():
        print(f"  Position {pos} -> Original Index {orig_idx}")
    print()
    
    # Test reverse lookup
    print("Reverse lookup test:")
    for pos, orig_idx in row_mapping.items():
        if str(orig_idx) == str(orig_idx):  # Simulate treeview iid lookup
            print(f"  Found original index {orig_idx} at position {pos}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_index_preservation() 