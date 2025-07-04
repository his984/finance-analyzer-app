# Bug Fix Summary

## Problem Description

The application was failing to correctly update or delete rows when filters were applied. This was due to a critical bug in the `gui/app_ui.py` file, where the methods for updating and deleting rows were using an incorrect variable to identify the selected row.

## Root Cause Analysis

The `update_row_data` and `delete_selected_row` methods were relying on `self.controller.currently_selected_row_index`, but this variable was never assigned a value when a row was selected. The correct variable to use was `self.controller.currently_selected_original_index`, which is properly set in the `table_row_selected` method.

## Solution Implemented

### 1. **Refactored `update_row_data` and `delete_selected_row`**

The `update_row_data` and `delete_selected_row` methods were refactored to use the correct `self.controller.currently_selected_original_index` variable. This ensures that the correct row is always identified and modified, regardless of whether filters are applied.

### 2. **Updated `reset_control_panel`**

The `reset_control_panel` method was updated to properly clear the `currently_selected_original_index` variable. This prevents any potential issues with stale or incorrect index references.

## Files Modified

- `gui/app_ui.py`: Corrected the variable used to identify the selected row in the `update_row_data` and `delete_selected_row` methods, and updated the `reset_control_panel` method to properly clear the index.
