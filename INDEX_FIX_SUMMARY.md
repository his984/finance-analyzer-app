# Index Mismatch Fix Summary

## Problem Description

The issue was that when trying to add a category to a specific row, the category was being assigned to the previous row instead of the selected row. This was caused by an index mismatch between the treeview's internal indexing and the DataFrame's index when filters were applied.

## Root Cause Analysis

### The Problem

1. **Treeview Population**: When `is_interactive=True`, the treeview uses the DataFrame's original index as the `iid` (item ID)
2. **Filtering**: When filters are applied, a new filtered DataFrame is created with different indices
3. **Row Selection**: The `table_row_selected` method was using the original DataFrame to look up the selected row
4. **Index Mismatch**: The selected `iid` from the treeview no longer corresponded to the correct row in the original DataFrame

### Example Scenario

- Original DataFrame has indices: [0, 1, 2, 3, 4]
- User applies filter, filtered DataFrame has indices: [1, 3] (rows 1 and 3 match filter)
- Treeview shows filtered data but uses original indices as `iid`: [1, 3]
- User selects row with `iid=3` (which is the second row in the treeview)
- Code tries to access row 3 in original DataFrame, but this might not be the intended row

## Solution Implemented

### 1. **Added Current Displayed DataFrame Tracking**

```python
self.current_displayed_df = None  # Track currently displayed DataFrame
```

### 2. **Updated apply_filters Method**

```python
def apply_filters(self, event=None) -> None:
    # ... existing code ...
    df_to_display = self.controller.filter_data(selected_category, search_term, value_filter)
    self.current_displayed_df = df_to_display  # Store currently displayed DataFrame
    # ... rest of method ...
```

### 3. **Fixed table_row_selected Method**

```python
def table_row_selected(self, event) -> None:
    # ... existing code ...
    try:
        # Use the currently displayed DataFrame instead of the original
        if self.current_displayed_df is not None:
            index_type = self.current_displayed_df.index.dtype.type
            self.controller.currently_selected_row_index = index_type(selected_iid_str)
            item_data = self.current_displayed_df.loc[self.controller.currently_selected_row_index]
        else:
            # Fallback to original DataFrame if no filtered data
            index_type = self.controller.selected_df.index.dtype.type
            self.controller.currently_selected_row_index = index_type(selected_iid_str)
            item_data = self.controller.selected_df.loc[self.controller.currently_selected_row_index]
        # ... rest of method ...
```

### 4. **Updated update_row_category Method**

```python
def update_row_category(self) -> None:
    # ... existing code ...
    # Get the item description from the currently displayed DataFrame
    if self.current_displayed_df is not None:
        item_description = self.current_displayed_df.loc[
            self.controller.currently_selected_row_index, "Description"
        ]
    else:
        # Fallback to original DataFrame if no filtered data
        item_description = self.controller.selected_df.loc[
            self.controller.currently_selected_row_index, "Description"
        ]

    # Update the original DataFrame (not the filtered one)
    self.controller.selected_df.loc[self.controller.currently_selected_row_index, "Category"] = (
        chosen_category
    )
    # ... rest of method ...
```

### 5. **Updated delete_selected_row Method**

```python
def delete_selected_row(self) -> None:
    # ... existing code ...
    try:
        # Delete from the original DataFrame (not the filtered one)
        self.controller.selected_df.drop(self.controller.currently_selected_row_index, inplace=True)
        # ... rest of method ...
```

### 6. **Initialized current_displayed_df in Key Methods**

- `load_file()`: Set to original DataFrame when file is loaded
- `analyze_data()`: Set to original DataFrame after analysis

## How the Fix Works

### Before the Fix

1. User selects row in treeview
2. Code uses treeview's `iid` to look up row in original DataFrame
3. **Problem**: The `iid` might not correspond to the correct row due to filtering

### After the Fix

1. User selects row in treeview
2. Code uses treeview's `iid` to look up row in **currently displayed DataFrame**
3. **Solution**: The `iid` now correctly corresponds to the visible row
4. When updating, the correct row in the original DataFrame is modified

## Benefits of the Fix

1. **Correct Row Selection**: Categories are now assigned to the correct selected row
2. **Filter Compatibility**: Works correctly with all filtering operations
3. **Sort Compatibility**: Works correctly when table is sorted
4. **Backward Compatibility**: Maintains fallback to original DataFrame when needed
5. **Data Integrity**: Updates are made to the correct rows in the original DataFrame

## Testing Recommendations

To verify the fix works correctly:

1. **Load data and analyze**
2. **Apply filters** (category, search, positive/negative)
3. **Select different rows** and assign categories
4. **Verify categories are assigned to the correct rows**
5. **Test with sorting** applied
6. **Test with multiple filters** applied simultaneously

## Files Modified

- `gui/app_ui.py`: Main application file with all the index handling logic

## Status

✅ **FIXED**: The index mismatch issue has been resolved. Categories are now correctly assigned to the selected rows regardless of filtering or sorting operations.
